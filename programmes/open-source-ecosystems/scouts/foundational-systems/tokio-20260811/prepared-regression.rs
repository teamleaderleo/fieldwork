// Prepared target-native regression for tokio/tests/fs_dir.rs.
//
// Evidence class in Fieldwork: target-test-prepared only.
// This has not been executed against the exact target checkout yet.

use std::future::Future;
use std::pin::pin;
use std::task::{Context, Poll, RawWaker, RawWakerVTable, Waker};

use tempfile::tempdir;
use tokio::fs;

fn noop_waker() -> Waker {
    fn no_op(_: *const ()) {}
    fn clone(_: *const ()) -> RawWaker {
        RawWaker::new(std::ptr::null(), &VTABLE)
    }
    static VTABLE: RawWakerVTable = RawWakerVTable::new(clone, no_op, no_op, no_op);

    // SAFETY: every vtable operation ignores the null data pointer.
    unsafe { Waker::from_raw(RawWaker::new(std::ptr::null(), &VTABLE)) }
}

#[test]
fn read_dir_refill_after_runtime_shutdown_must_not_park_forever() {
    let base = tempdir().unwrap();

    // read_dir.rs currently preloads CHUNK_SIZE == 32 entries. Create enough
    // entries to guarantee that the next call after draining 32 needs a refill.
    for idx in 0..64 {
        std::fs::write(base.path().join(format!("entry-{idx:02}")), b"x").unwrap();
    }

    let rt = tokio::runtime::Builder::new_multi_thread()
        .worker_threads(1)
        .enable_all()
        .build()
        .unwrap();
    let handle = rt.handle().clone();

    let mut dir = rt.block_on(fs::read_dir(base.path())).unwrap();

    // Drain exactly the chunk populated by fs::read_dir while the blocking pool
    // is alive. None of these calls should need another blocking task.
    for _ in 0..32 {
        assert!(rt.block_on(dir.next_entry()).unwrap().is_some());
    }

    // Shut down the blocking pool, then re-enter this runtime's context so the
    // internal refill spawn resolves against the same shut-down pool.
    rt.shutdown_background();
    let _guard = handle.enter();

    let mut next = pin!(dir.next_entry());
    let waker = noop_waker();
    let mut cx = Context::from_waker(&waker);

    // Candidate expected contract: an internal blocking-spawn failure should be
    // surfaced as an error (or another terminal Ready result), not stored as a
    // JoinHandle that Tokio documents will never resolve during shutdown.
    match next.as_mut().poll(&mut cx) {
        Poll::Ready(Err(_)) => {}
        Poll::Ready(Ok(value)) => panic!(
            "unexpected successful post-shutdown directory result: {value:?}"
        ),
        Poll::Pending => panic!(
            "ReadDir refill parked on a non-mandatory blocking JoinHandle after shutdown"
        ),
    }
}
