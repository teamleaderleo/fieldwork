# Polars cancellation probe lockfile receipt

Parent issue: #122

Carrier: PR #219

State: exact generated dependency receipt retained; target execution belongs to the earlier immutable execution head

## Exact source

- Fieldwork target-executed head: `fe24af28d966e9459ff5a268bffd6b44b768251c`
- Polars source: `36e414b4cb1e74e7a171995b35b83c1163974324`
- Polars object-store fork: `f50a6e5c564b2b5933eca15cd20ff9b5614374a1`
- successful workflow: `30623286118`
- successful job: `91132573948`
- artifact: `8790351996`
- artifact digest: `sha256:fc233e0f31d1b7c6cc74d2c1da9e96dbb4d782ab399a34ff4266cc73ce1b2abb`

The artifact contained the exact `Cargo.lock` generated before the successful locked Polars build and execution.

## Retained representation

The lockfile is retained as deterministic gzip bytes, base64-encoded and split into four UTF-8 text parts outside the retired workflow's trigger path.

Original lockfile:

- filename: `issue122-polars-Cargo.lock`
- bytes: `82682`
- lines: `3521`
- SHA-256: `1ab03b86603c306e792330c332eee1d6afb1c4b382a0eab0fc8a3233a636d2e3`

Deterministic gzip representation (`gzip -n -9`):

- SHA-256: `9abdf9f2934e58c61e9d988cbcc5449f44f3ce050df5386cd78776f4fc7cc077`

Complete base64 text:

- bytes: `26715`
- SHA-256: `ffa16fac870607a12bc3ec74cb936428f3df546634dc5ca48958e6aeaee65ece`

Parts, in order:

| Part | Bytes | SHA-256 |
| --- | ---: | --- |
| `issue122-polars-Cargo.lock.gz.b64.part00` | 7000 | `466571a6ede77684c78ab7c03149003ccee37f2ac9ce301c4de8b65d52a2499b` |
| `issue122-polars-Cargo.lock.gz.b64.part01` | 7000 | `fcea4ecd6d9d3b74a90eb0076934787665deff717213ef746d6c330278574ed3` |
| `issue122-polars-Cargo.lock.gz.b64.part02` | 7000 | `94b66b1a166cf2899e50d7d9230bd0af8e992c22be550d1e87d95b94d46446ec` |
| `issue122-polars-Cargo.lock.gz.b64.part03` | 5715 | `8badc090e937a784347f948b2df6e0e1d4f733bb7d2be8cbc805d86f67c7de87` |

## Reconstruction

From this directory:

```sh
cat \
  issue122-polars-Cargo.lock.gz.b64.part00 \
  issue122-polars-Cargo.lock.gz.b64.part01 \
  issue122-polars-Cargo.lock.gz.b64.part02 \
  issue122-polars-Cargo.lock.gz.b64.part03 \
  > issue122-polars-Cargo.lock.gz.b64

printf '%s  %s\n' \
  ffa16fac870607a12bc3ec74cb936428f3df546634dc5ca48958e6aeaee65ece \
  issue122-polars-Cargo.lock.gz.b64 \
  | sha256sum --check

base64 --decode issue122-polars-Cargo.lock.gz.b64 \
  > issue122-polars-Cargo.lock.gz

printf '%s  %s\n' \
  9abdf9f2934e58c61e9d988cbcc5449f44f3ce050df5386cd78776f4fc7cc077 \
  issue122-polars-Cargo.lock.gz \
  | sha256sum --check

gzip --decompress --stdout issue122-polars-Cargo.lock.gz \
  > issue122-polars-Cargo.lock

printf '%s  %s\n' \
  1ab03b86603c306e792330c332eee1d6afb1c4b382a0eab0fc8a3233a636d2e3 \
  issue122-polars-Cargo.lock \
  | sha256sum --check
```

## Evidence boundary

This retained representation proves the exact generated dependency lock bytes from artifact `8790351996`. It does not mean Polars or DataFusion executed again on the later receipt-transfer commits.

The behavioral result remains bound to target-executed head `fe24af28...`, run `30623286118`, and job `91132573948`. The subsequent commits only transfer durable evidence and retire temporary execution machinery.
