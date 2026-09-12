import Foundation
import Dispatch

final class Tunnel: @unchecked Sendable {
    let name: String
    let q: DispatchQueue
    let onFatal: @Sendable (String) -> Void
    var stopped = false
    var stopCount = 0
    init(_ name: String, onFatal: @escaping @Sendable (String) -> Void) {
        self.name = name; self.q = DispatchQueue(label: "tunnel.\(name)"); self.onFatal = onFatal
    }
    func beginFailure(_ entered: DispatchSemaphore, _ release: DispatchSemaphore, _ callbackQueued: DispatchSemaphore) {
        q.async {
            guard !self.stopped else { return }
            self.stopped = true
            entered.signal()
            release.wait()
            self.onFatal("A transport failed")
            callbackQueued.signal()
        }
    }
    func stop() { q.sync { self.stopped = true; self.stopCount += 1 } }
}

final class Broker: @unchecked Sendable {
    let q = DispatchQueue(label: "broker")
    var tunnel: Tunnel?
    var ready: String?
    let staleDone = DispatchSemaphore(value: 0)
    let acquireDone = DispatchSemaphore(value: 0)

    func make(_ name: String, generationGuard: Bool, generation: UUID) -> Tunnel {
        Tunnel(name) { [weak self] detail in
            guard let self else { return }
            self.q.async {
                if generationGuard && self.currentGeneration != generation {
                    print("SAFE_DROP stale=A current=\(self.ready ?? "nil")")
                    self.staleDone.signal(); return
                }
                guard let current = self.tunnel else { self.staleDone.signal(); return }
                current.stop()
                print("STALE_FATAL_STOPPED \(current.name): \(detail)")
                self.tunnel = nil; self.ready = nil; self.currentGeneration = nil
                self.staleDone.signal()
            }
        }
    }
    var currentGeneration: UUID?

    func installInitial(_ t: Tunnel, generation: UUID) { q.sync { tunnel=t; ready=t.name; currentGeneration=generation } }

    func releaseLastLease(_ releaseEntered: DispatchSemaphore) {
        q.async {
            releaseEntered.signal()
            if let old = self.tunnel { old.stop() }
            self.tunnel = nil; self.ready = nil; self.currentGeneration=nil
            print("A_ENTRY_REMOVED")
        }
    }

    func acquireSuccessor(_ b: Tunnel, generation: UUID) {
        q.async {
            self.tunnel=b; self.ready=b.name; self.currentGeneration=generation
            print("B_READY")
            self.acquireDone.signal()
        }
    }
}

func run(_ guarded: Bool) {
    print(guarded ? "=== CONTROL_GENERATION_GUARD ===" : "=== CURRENT_KEY_ONLY ===")
    let broker=Broker(); let ga=UUID(); let gb=UUID()
    let a=broker.make("A", generationGuard: guarded, generation: ga)
    let b=broker.make("B", generationGuard: guarded, generation: gb)
    broker.installInitial(a, generation: ga)
    let failureEntered=DispatchSemaphore(value:0), releaseFailure=DispatchSemaphore(value:0), callbackQueued=DispatchSemaphore(value:0), releaseEntered=DispatchSemaphore(value:0)
    a.beginFailure(failureEntered, releaseFailure, callbackQueued)
    failureEntered.wait()
    broker.releaseLastLease(releaseEntered)
    releaseEntered.wait()
    broker.acquireSuccessor(b, generation: gb)
    releaseFailure.signal()
    callbackQueued.wait()
    broker.acquireDone.wait()
    broker.staleDone.wait()
    broker.q.sync { print("FINAL_CURRENT \(broker.ready ?? "nil") B_STOP_COUNT \(b.stopCount)") }
}

run(false)
run(true)
