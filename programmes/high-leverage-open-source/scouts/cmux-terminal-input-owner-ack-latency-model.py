#!/usr/bin/env python3
"""Model cmux terminal-input acknowledgement latency and throughput.

This is a deterministic queueing model, not a production benchmark. It compares:

* accepted: return once the local sender has submitted the frame;
* stop_wait: one write is submitted, delivered, acknowledged, then the next starts;
* pipelined_ack: multiple request/ack writes may remain outstanding;
* cumulative_ack: the same bounded pipeline, but one ACK can cover a group.

All timing inputs are explicit parameters. The model intentionally does not claim
a fixed Unix-socket RTT or PTY write cost for cmux.
"""

from __future__ import annotations

import argparse
from collections import deque
from dataclasses import dataclass
from statistics import median
import socket
import threading
import time
from typing import Iterable


@dataclass(frozen=True)
class Parameters:
    writes: int
    submit_us: float
    ipc_rtt_us: float
    owner_us: float
    window: int
    ack_every: int


@dataclass(frozen=True)
class Result:
    name: str
    makespan_us: float
    rate_per_second: float
    p50_latency_us: float
    p95_latency_us: float
    ack_frames: int


def percentile(values: Iterable[float], fraction: float) -> float:
    ordered = sorted(values)
    if not ordered:
        return 0.0
    position = (len(ordered) - 1) * fraction
    lower = int(position)
    upper = min(lower + 1, len(ordered) - 1)
    weight = position - lower
    return ordered[lower] * (1.0 - weight) + ordered[upper] * weight


def simulate(params: Parameters, mode: str) -> Result:
    if params.writes < 1:
        raise ValueError("writes must be positive")
    if params.submit_us < 0 or params.ipc_rtt_us < 0 or params.owner_us < 0:
        raise ValueError("timings must be non-negative")
    if params.window < 1:
        raise ValueError("window must be positive")
    if params.ack_every < 1:
        raise ValueError("ack_every must be positive")

    one_way_us = params.ipc_rtt_us / 2.0
    sender_free_us = 0.0
    owner_free_us = 0.0
    starts = [0.0] * params.writes
    completions = [0.0] * params.writes
    outstanding: deque[int] = deque()
    cumulative_group: list[int] = []
    ack_frames = 0

    for index in range(params.writes):
        if mode in {"pipelined_ack", "cumulative_ack"}:
            while len(outstanding) >= params.window:
                sender_free_us = max(sender_free_us, completions[outstanding[0]])
                while outstanding and completions[outstanding[0]] <= sender_free_us:
                    outstanding.popleft()

        if mode == "stop_wait" and index:
            sender_free_us = max(sender_free_us, completions[index - 1])

        starts[index] = sender_free_us
        send_done_us = sender_free_us + params.submit_us
        sender_free_us = send_done_us

        if mode == "accepted":
            completions[index] = send_done_us
            continue

        owner_arrival_us = send_done_us + one_way_us
        owner_start_us = max(owner_arrival_us, owner_free_us)
        owner_done_us = owner_start_us + params.owner_us
        owner_free_us = owner_done_us

        if mode in {"stop_wait", "pipelined_ack"}:
            completions[index] = owner_done_us + one_way_us
            ack_frames += 1
            if mode == "pipelined_ack":
                outstanding.append(index)
            continue

        if mode == "cumulative_ack":
            cumulative_group.append(index)
            outstanding.append(index)
            if len(cumulative_group) == params.ack_every or index == params.writes - 1:
                ack_arrival_us = owner_done_us + one_way_us
                ack_frames += 1
                for covered in cumulative_group:
                    completions[covered] = ack_arrival_us
                cumulative_group.clear()
            continue

        raise ValueError(f"unknown mode: {mode}")

    latencies = [
        completions[index] - starts[index]
        for index in range(params.writes)
    ]
    makespan_us = max(completions)
    rate = params.writes / (makespan_us / 1_000_000.0) if makespan_us else 0.0
    return Result(
        name=mode,
        makespan_us=makespan_us,
        rate_per_second=rate,
        p50_latency_us=percentile(latencies, 0.50),
        p95_latency_us=percentile(latencies, 0.95),
        ack_frames=ack_frames,
    )


def socketpair_rtt(iterations: int) -> tuple[float, float, float]:
    """Characterize this Python runtime's local socketpair echo RTT.

    This is deliberately separate from the cmux model. Python scheduling,
    interpreter overhead, runner load, and this host kernel all contribute.
    """
    if iterations < 1:
        raise ValueError("iterations must be positive")

    left, right = socket.socketpair()

    def echo() -> None:
        try:
            for _ in range(iterations):
                payload = right.recv(1)
                if not payload:
                    return
                right.sendall(payload)
        finally:
            right.close()

    worker = threading.Thread(target=echo, name="socketpair-echo", daemon=True)
    worker.start()
    samples_us: list[float] = []
    try:
        for _ in range(iterations):
            started_ns = time.perf_counter_ns()
            left.sendall(b"x")
            payload = left.recv(1)
            if payload != b"x":
                raise RuntimeError("socketpair echo changed the payload")
            samples_us.append((time.perf_counter_ns() - started_ns) / 1_000.0)
    finally:
        left.close()
        worker.join()

    return (
        median(samples_us),
        percentile(samples_us, 0.95),
        percentile(samples_us, 0.99),
    )


def print_results(params: Parameters) -> None:
    print(
        "assumptions:"
        f" writes={params.writes}"
        f" submit_us={params.submit_us:g}"
        f" ipc_rtt_us={params.ipc_rtt_us:g}"
        f" owner_us={params.owner_us:g}"
        f" window={params.window}"
        f" ack_every={params.ack_every}"
    )
    print()
    print(
        f"{'mode':<16}"
        f"{'makespan ms':>14}"
        f"{'writes/s':>14}"
        f"{'p50 us':>12}"
        f"{'p95 us':>12}"
        f"{'acks':>10}"
    )
    for mode in ("accepted", "stop_wait", "pipelined_ack", "cumulative_ack"):
        result = simulate(params, mode)
        print(
            f"{result.name:<16}"
            f"{result.makespan_us / 1000.0:>14.3f}"
            f"{result.rate_per_second:>14.1f}"
            f"{result.p50_latency_us:>12.1f}"
            f"{result.p95_latency_us:>12.1f}"
            f"{result.ack_frames:>10d}"
        )


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--writes", type=int, default=5_000)
    parser.add_argument(
        "--submit-us",
        type=float,
        default=5.0,
        help="sender time to serialize/enqueue one local frame",
    )
    parser.add_argument(
        "--ipc-rtt-us",
        type=float,
        default=100.0,
        help="assumed local IPC round-trip, excluding owner work",
    )
    parser.add_argument(
        "--owner-us",
        type=float,
        default=15.0,
        help="assumed terminal-owner PTY write/flush service time per write",
    )
    parser.add_argument("--window", type=int, default=256)
    parser.add_argument(
        "--ack-every",
        type=int,
        default=16,
        help="writes covered by one cumulative ACK",
    )
    parser.add_argument(
        "--bench-socketpair",
        type=int,
        metavar="N",
        help="also measure N one-byte Python socketpair echo RTTs on this host",
    )
    args = parser.parse_args()

    params = Parameters(
        writes=args.writes,
        submit_us=args.submit_us,
        ipc_rtt_us=args.ipc_rtt_us,
        owner_us=args.owner_us,
        window=args.window,
        ack_every=args.ack_every,
    )
    print_results(params)

    if args.bench_socketpair:
        p50, p95, p99 = socketpair_rtt(args.bench_socketpair)
        print()
        print(
            "python socketpair characterization"
            f" n={args.bench_socketpair}"
            f" median_us={p50:.3f}"
            f" p95_us={p95:.3f}"
            f" p99_us={p99:.3f}"
        )
        print(
            "note: this is host/Python characterization, not a cmux target benchmark"
        )


if __name__ == "__main__":
    main()
