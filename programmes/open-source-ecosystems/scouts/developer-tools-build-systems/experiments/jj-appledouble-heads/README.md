# Jujutsu AppleDouble table-head experiment

State: `execution queued`

Parent scout: `#561`  
Exact target: `jj-vcs/jj@3a650c3a68aadfa693b193ffb3176fd09b824c86`  
Exact `lib/src/stacked_table.rs` blob: `47dd3e95d1caedf638b7b74422e0dd8d13214fd1`  
Public upstream issue: `jj-vcs/jj#9775`  
Upstream contact authorized: `false`

## In simple words

Jujutsu's table store scans every filename in its `heads` directory and currently tries to load each one as a real content-addressed table segment. macOS archive sidecars use names beginning with `._`, so an extracted sidecar can become false metadata authority and break ordinary repository loading.

## Exact experiment

The target-native fixture runs in two stages against a disposable exact checkout.

### Current source characterization

1. create a valid table store and head;
2. add `._<valid-head-name>` under the store's `heads` directory;
3. reload the store;
4. require the current loader to return a `LoadSegment`-class error naming the sidecar.

### Bounded candidate comparison

Filter head directory entries to exact 128-character lowercase hexadecimal segment identities before loading them, then prove:

1. the AppleDouble sidecar is ignored;
2. a 128-character non-hex filename is ignored;
3. the original valid head still loads;
4. a truncated file with a valid-looking 128-character lowercase hexadecimal name still raises a load error.

The fourth control prevents the candidate from hiding actual segment corruption.

## Decision rule

Promote the filter only if it separates filename authority from content integrity: platform-generated and otherwise invalid names must be non-authoritative, while valid-looking corrupt segment identities remain errors.

If current source already ignores the sidecar, stop as not reproduced. If the filter hides valid-name corruption, reject the candidate.

## Evidence boundary

This experiment exercises the internal `TableStore` directly. It does not reproduce a complete archived Jujutsu repository or claim all AppleDouble placements are harmless. A later source candidate must map other metadata directories and run the repository's ordinary format, clippy, and workspace test gates.
