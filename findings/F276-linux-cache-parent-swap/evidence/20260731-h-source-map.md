# H source map — caching-proxy pathname replacement boundary

Date: 2026-07-31  
Worker: H  
Linux source: `teamleaderleo/linux-fieldwork@ed49c01a85e9d363626db5d2973a33b67209e13b`  
Prepared probe head: `dabe79cefb6062e20dc6201556b5f541a8470bbc`

## In simple words

The cache candidate checks one resolved path and later uses the same text as a new filesystem lookup. A same-UID process can replace a checked parent or final component before that lookup. The prepared matrix pauses at the exact gaps, records parent and final-component behavior separately, restores the original state, reruns against the same roots, and repeats the full matrix under optimized Python.

## Source operation sequence

### Validation

`investigations/caching-proxy-complete-stack/compose_impl.py` generates `request_context()`:

1. parse request and host authority;
2. reject percent escapes, backslashes, NUL, empty, dot, and parent components;
3. resolve the configured root;
4. resolve the candidate pathname;
5. require a strict descendant;
6. return an ordinary `pathlib.Path`.

### Old-cache read

The generated handler retains the imported cache-hit sequence:

1. call `oldpath.exists()`;
2. obtain size by pathname;
3. open by pathname;
4. stream to client;
5. copy into the new cache destination.

The read barriers wrap `request_context()` and pause on its second call, after old and new candidates are computed but before the handler performs its first cache existence check. One test replaces the parent directory; another replaces only the final object name.

### New-cache publication

The atomic patch:

1. derives a random sibling pathname with `path.with_name()`;
2. opens it using pathname-based `os.open(... O_EXCL ...)`;
3. yields the file object;
4. closes it;
5. publishes with pathname-based `os.replace(temporary, path)`;
6. removes a surviving temporary pathname in `finally`.

The publication barriers wrap `cache_destination()` and pause before the original context manager re-traverses the validated parent. One test replaces the parent directory; a control creates only a final-name symlink and distinguishes replacing that symlink from following its target.

## Distinguishing filesystem transitions

Parent replacement:

```text
validated parent: <cache>/pool
rename to:        <cache>/pool-validated
replacement:      <cache>/pool -> <outside>
```

Final-component replacement:

```text
validated object: <cache>/pool/object.deb
rename to:        <cache>/pool/object-validated.deb
replacement:      <cache>/pool/object.deb -> <outside>/object.deb
```

Read case outside state:

```text
<outside>/object.deb = outside-cache-secret
```

Publication case outside state:

```text
<outside>/sentinel = preserve me
```

A confined implementation uses the checked directory identity or rejects the mutation. A pathname-retraversal implementation can read or publish through a replacement parent. Final publication may differ because `os.replace()` can replace the symlink entry itself while preserving its target.

## Rerun and optimized controls

After each mutated case, the test restores the checked component, removes or resets any raced cache object, sends another request against the same cache roots, and asserts normal bytes, origin ownership, and hidden-temporary cleanup.

The test file also spawns itself with `python -O`. A child marker skips only the recursive launcher; all inherited composed tests and replacement probes remain active in the optimized interpreter.

## Evidence limits

The barriers are deliberate fault injection. They establish operation ordering and consequence on Linux when they run; they do not measure natural race frequency. The outside directories remain inside one disposable temporary tree for cleanup while remaining outside the validated old or new cache root.

The exact baseline does not separately force a replacement before the primary new-cache hit or before recursive parent creation. Those operations remain part of the candidate-wide path audit if the retained probes establish the underlying loss of authority.

No public upstream interaction occurred.
