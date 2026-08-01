# Retained exact target patch series

## In simple words

The GitHub Actions artifact from target run `30642924979` contained one exact 27,268-byte patch. This directory stores that patch as four ordered text chunks so GitHub remains the durable continuation record.

Concatenating the chunks in lexical order reproduces the artifact byte-for-byte and yields SHA-256:

```text
d30874c96f8e39350b9d725c58a6034554c561b073cb04969849ff2778c09e88
```

## Identity

- Target repository: `upstash/box`
- Exact target base: `b55d832d6e3ae0156e32d21ea3863e231dfff9cd`
- Exact Fieldwork execution head: `1e7909da440ab631fcea11d4d3777d2bce107277`
- Workflow: `30642924979`
- Job: `91197101877`
- Artifact: `8798217638`
- Artifact digest: `sha256:5629a4706772b989c0ed2a88689569572d8c231eb23a19f468ed101adff1c3b4`
- Patch size: `27268` bytes
- Patch paths: `15` unique
- Patch stats: `471` additions, `27` deletions

## Ordered chunks

| Order | File | Bytes | SHA-256 |
| ---: | --- | ---: | --- |
| 1 | [`0001-python-parity-and-native-tests.patch`](./0001-python-parity-and-native-tests.patch) | 4966 | `9abbeaa709eb104ea76ba300ae3c336d887e02564a8be8f752b3fa75b56fade4` |
| 2 | [`0002-python-concurrency-tests.patch`](./0002-python-concurrency-tests.patch) | 6411 | `154fee690f67a824439665f88ef242fa213f5105794cfde2c4b294b51c7c6d33` |
| 3 | [`0003-python-runtime-and-generated-client.patch`](./0003-python-runtime-and-generated-client.patch) | 7050 | `deb003da31aa4b532a581eb67a87d4b8acf3dd3f58e8be6e05bd59c0e27445f7` |
| 4 | [`0004-typescript-receipt-and-tests.patch`](./0004-typescript-receipt-and-tests.patch) | 8841 | `46064f1a2cf64a8472763e15cd56dcc5940bac5148ffb436f05c5b8b639e46ef` |

## Reconstruction

From this directory:

```sh
cat \
  0001-python-parity-and-native-tests.patch \
  0002-python-concurrency-tests.patch \
  0003-python-runtime-and-generated-client.patch \
  0004-typescript-receipt-and-tests.patch \
  > target-executed-b55d832.patch

sha256sum target-executed-b55d832.patch
```

Expected result:

```text
d30874c96f8e39350b9d725c58a6034554c561b073cb04969849ff2778c09e88  target-executed-b55d832.patch
```

The split and reconstruction were verified locally on `2026-08-01`: concatenated bytes matched the downloaded artifact exactly.

## Current use

This series preserves the historical tested candidate. It remains research evidence, not the clean upstream source branch. The TypeScript stream-abort composition blocker described in [`../DEEP_DIVE.md`](../DEEP_DIVE.md) must be repaired and re-executed before source publication.
