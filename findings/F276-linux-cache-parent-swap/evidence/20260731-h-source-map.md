# H source map — caching-proxy parent-swap boundary

Date: 2026-07-31  
Worker: H  
Linux source: `teamleaderleo/linux-fieldwork@ed49c01a85e9d363626db5d2973a33b67209e13b`  
Prepared probe head: `66f0f6539d9ae7e714675f1f152e43a6fc2f4a5c`

## In simple words

The cache candidate checks one resolved path and later uses the same text as a new filesystem lookup. A rename-plus-symlink swap can change what that text names. The prepared test pauses at the two exact gaps so hosted Linux execution can decide whether reads and writes leave the cache root.

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

The prepared read barrier wraps `request_context()` and pauses on its second call, after old and new candidates are computed but before the handler performs its first cache existence check.

### New-cache publication

The atomic patch:

1. derives a random sibling pathname with `path.with_name()`;
2. opens it using pathname-based `os.open(... O_EXCL ...)`;
3. yields the file object;
4. closes it;
5. publishes with pathname-based `os.replace(temporary, path)`;
6. removes a surviving temporary pathname in `finally`.

The prepared publication barrier wraps `cache_destination()` and pauses before the original context manager re-traverses the validated parent.

## Distinguishing filesystem transition

For each race:

```text
validated parent: <cache>/pool
rename to:        <cache>/pool-validated
replacement:      <cache>/pool -> <outside>
```

Read case outside state:

```text
<outside>/object.deb = outside-cache-secret
```

Publication case outside state:

```text
<outside>/sentinel = preserve me
```

A confined implementation uses the checked directory identity or rejects the mutation. A pathname-retraversal implementation reads or publishes through the replacement symlink.

## Evidence limits

The barrier is deliberate fault injection. It proves operation ordering and consequence on Linux when it runs; it does not measure natural race frequency. The outside directory remains inside one disposable temporary tree for cleanup, while remaining outside the validated old or new cache root.

No public upstream interaction occurred.
