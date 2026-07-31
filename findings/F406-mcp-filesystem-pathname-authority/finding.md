# F406 — MCP filesystem pathname authority after validation

State: `research-active`  
Evidence class: `source-read / target-test-prepared`  
Owning issue: #406  
Initiative: #254  
Target: `modelcontextprotocol/servers@76d64c822f5125032f89eb71dbdb94e42b434821`  
Upstream contact authorized: no

## In simple words

The filesystem server checks a pathname, resolves symlinks, and confirms the result is inside an allowed directory. It then performs the actual filesystem operation later using the pathname again.

A directory can change between those two moments. If a validated parent is replaced with a symlink to an outside directory, a later pathname-based write can follow the new ancestor even though that ancestor was never validated.

The first target-native control uses temporary directories only and forces that ordering with no timing race.

## Consequence

A static symlink check can be correct while mutation authority still belongs to a pathname whose ancestors are mutable after validation. Final-component exclusivity and atomic rename do not pin ancestor directory identity.

The immediate claim is narrow: exact Linux/Node source composition for nonexistent-file creation through the repository's exported `validatePath()` and `writeFileContent()` functions. Create-directory, move, edit, dynamic roots, other platforms, production prevalence, and exploitability remain separate controls.

## Governing invariant

A mutation described as limited to allowed directories must act through the same directory authority that was validated. Re-resolving mutable ancestors after validation must not silently widen the operation beyond the allowed roots.

## Exact source map

Pinned source: `modelcontextprotocol/servers@76d64c822f5125032f89eb71dbdb94e42b434821`.

- `src/filesystem/lib.ts::validatePath()` performs a lexical allowed-root check.
- Existing targets are resolved with `fs.realpath()` and checked again.
- A nonexistent target validates the current real parent and then returns the original absolute child pathname.
- `src/filesystem/lib.ts::writeFileContent()` later calls `fs.writeFile(path, ..., { flag: "wx" })`.
- Existing targets use a sibling temporary pathname followed by `fs.rename(tempPath, filePath)`.
- `src/filesystem/index.ts` composes `validatePath()` with later `fs.mkdir()` and `fs.rename()` calls for create and move operations.
- MCP roots may replace the global allowed-directory set while the process remains active.

Existing path-validation tests cover traversal, prefix confusion, static symlinks, null bytes, Unicode, and platform syntax. No control was found for ancestor replacement after validation.

## First exact comparison

The prepared Linux test has three cases:

1. **Stable parent:** validation plus `writeFileContent()` creates the file inside the allowed directory.
2. **Static outside symlink:** validation rejects a parent already linked outside the allowed directory.
3. **Post-validation ancestor swap:** validation succeeds while the parent is inside; the test renames that directory aside, installs an outside-pointing directory symlink at the original pathname, calls the real write helper, and records whether the bytes appear outside.

The test uses one temporary root, no external files, no credentials, and deterministic cleanup.

## Alternatives to compare after characterization

### A — descriptor-relative ownership

Open and retain a directory capability, then perform final-component operations relative to that descriptor using an `openat`-style primitive. This best preserves the validated ancestor identity, but ordinary Node APIs may not expose a portable complete implementation.

### B — native helper boundary

Use a small native or platform-specific helper for descriptor-relative mutation. This can close the primitive gap at the cost of packaging, portability, and maintenance.

### C — bounded revalidation

Revalidate immediately before and after mutation and roll back or fail on movement. This reduces exposure but cannot fully eliminate the race between the final check and pathname syscall.

### D — explicit threat-model limit

Document that allowed roots protect against static path/symlink selection but do not defend against a concurrent local actor that can replace ancestors. This may be honest when the runtime cannot provide stronger primitives, but it changes the meaning operators can safely assign to the boundary.

## Current decision

Execute the deterministic write characterization before selecting a repair family. A target result showing outside creation establishes a real ancestor-identity gap for that exact composition. A denial or inside-only result rejects the current hypothesis and stops expansion unless another operation supplies different evidence.

## Claim boundary

Established now:

- source uses check-then-pathname-operation composition;
- final-component `wx` protection does not visibly bind ancestor identity in source;
- existing tests do not cover the prepared ordering.

Pending execution:

- actual outside-file creation under the forced Linux ancestor swap;
- stable and static-symlink controls;
- package build and existing focused regression.

Not claimed:

- public exploitability;
- production prevalence or impact;
- cross-platform behavior;
- create/move/edit escape behavior;
- dynamic-root revocation semantics;
- a portable complete repair;
- upstream acceptance.

## Exact next transition

Run the one-workflow exact-source carrier. On success, retain the log and receipt, remove the workflow from the canonical finding generation, then decide whether create/move/root-currentness controls add distinct evidence.

No merge, release, deployment, credential, private-data access, spending, or public-upstream interaction is authorized.