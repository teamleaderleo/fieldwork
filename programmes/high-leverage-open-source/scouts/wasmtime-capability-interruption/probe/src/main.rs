use std::future::{self, Future};
use std::pin::Pin;
use std::sync::Arc;
use std::sync::atomic::{AtomicBool, Ordering};
use std::task::{Context, Poll, Waker};
use std::time::Duration;

use anyhow::{Context as _, Result, ensure};
use wasmtime::{Config, Engine, Func, FuncType, Instance, Module, Store, StoreLimitsBuilder};

#[derive(Clone, Default)]
struct HostEffectState {
    committed: Arc<AtomicBool>,
    future_dropped: Arc<AtomicBool>,
}

struct DropMarker(Arc<AtomicBool>);

impl Drop for DropMarker {
    fn drop(&mut self) {
        self.0.store(true, Ordering::SeqCst);
    }
}

fn async_engine() -> Result<Engine> {
    let mut config = Config::new();
    config.async_support(true);
    config.epoch_interruption(true);
    Engine::new(&config).context("create async Wasmtime engine")
}

async fn epoch_interrupts_guest_loop() -> Result<()> {
    let engine = async_engine()?;
    let module = Module::new(
        &engine,
        r#"
            (module
                (func (export "run")
                    (loop $forever
                        br $forever)))
        "#,
    )?;
    let mut store = Store::new(&engine, ());
    store.set_epoch_deadline(1);
    store.epoch_deadline_trap();

    let instance = Instance::new_async(&mut store, &module, &[]).await?;
    let run = instance.get_typed_func::<(), ()>(&mut store, "run")?;

    let interrupt_engine = engine.clone();
    let interrupter = std::thread::spawn(move || {
        std::thread::sleep(Duration::from_millis(50));
        interrupt_engine.increment_epoch();
    });

    let result = run.call_async(&mut store, ()).await;
    interrupter.join().expect("epoch interrupter panicked");
    ensure!(result.is_err(), "infinite guest loop completed instead of trapping");
    Ok(())
}

async fn dropping_call_future_preserves_committed_host_effect() -> Result<()> {
    let engine = async_engine()?;
    let mut store = Store::new(&engine, ());
    let state = HostEffectState::default();
    let host_state = state.clone();

    let host = Func::new_async(
        &mut store,
        FuncType::new(&engine, [], []),
        move |_caller, _params, _results| {
            let host_state = host_state.clone();
            Box::new(async move {
                host_state.committed.store(true, Ordering::SeqCst);
                let drop_marker = DropMarker(host_state.future_dropped.clone());
                let _ = &drop_marker;
                future::pending::<()>().await;
                #[allow(unreachable_code)]
                Ok(())
            })
        },
    );

    let mut call: Pin<Box<_>> = Box::pin(host.call_async(&mut store, &[], &mut []));
    let mut context = Context::from_waker(Waker::noop());
    ensure!(
        matches!(call.as_mut().poll(&mut context), Poll::Pending),
        "async host call did not suspend"
    );
    ensure!(
        state.committed.load(Ordering::SeqCst),
        "synthetic host effect was not committed before suspension"
    );

    drop(call);

    ensure!(
        state.future_dropped.load(Ordering::SeqCst),
        "dropping the Wasmtime call did not drop the suspended host future"
    );
    ensure!(
        state.committed.load(Ordering::SeqCst),
        "future cancellation incorrectly erased the committed-effect marker"
    );
    Ok(())
}

async fn resource_limit_denial_and_trap_are_distinct() -> Result<()> {
    let engine = async_engine()?;
    let module = Module::new(
        &engine,
        r#"
            (module
                (memory 1 2)
                (func (export "grow") (result i32)
                    i32.const 1
                    memory.grow))
        "#,
    )?;

    let ordinary_limits = StoreLimitsBuilder::new().memory_size(65_536).build();
    let mut ordinary_store = Store::new(&engine, ordinary_limits);
    ordinary_store.limiter(|limits| limits);
    let ordinary_instance = Instance::new_async(&mut ordinary_store, &module, &[]).await?;
    let ordinary_grow =
        ordinary_instance.get_typed_func::<(), i32>(&mut ordinary_store, "grow")?;
    let ordinary_result = ordinary_grow.call_async(&mut ordinary_store, ()).await?;
    ensure!(
        ordinary_result == -1,
        "ordinary denied memory.grow returned {ordinary_result}, expected -1"
    );

    let trapping_limits = StoreLimitsBuilder::new()
        .memory_size(65_536)
        .trap_on_grow_failure(true)
        .build();
    let mut trapping_store = Store::new(&engine, trapping_limits);
    trapping_store.limiter(|limits| limits);
    let trapping_instance = Instance::new_async(&mut trapping_store, &module, &[]).await?;
    let trapping_grow =
        trapping_instance.get_typed_func::<(), i32>(&mut trapping_store, "grow")?;
    let trapping_result = trapping_grow.call_async(&mut trapping_store, ()).await;
    ensure!(
        trapping_result.is_err(),
        "trap-on-grow-failure returned normally"
    );
    Ok(())
}

#[tokio::main]
async fn main() -> Result<()> {
    epoch_interrupts_guest_loop().await?;
    dropping_call_future_preserves_committed_host_effect().await?;
    resource_limit_denial_and_trap_are_distinct().await?;

    println!("PASS: epoch interruption traps an infinite guest loop");
    println!("PASS: dropping an async call drops the host future but not a committed effect");
    println!("PASS: resource-limit denial and trap policy remain distinguishable");
    Ok(())
}
