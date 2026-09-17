# F406 — MCP filesystem pathname authority after validation

State: `comparative-evaluation-active`  
Evidence class: `source-read / target-executed-local`  
Owning issue: #406  
Initiative: #254  
Target: `modelcontextprotocol/servers@76d64c822f5125032f89eb71dbdb94e42b434821`  
Upstream contact authorized: no

## In simple words

The filesystem server validates a pathname and its current symlink target, then later performs the mutation through the pathname again.

Exact Linux execution proves the parent directory can change between those moments. After a nonexistent child was validated inside the allowed root, the test renamed its parent aside and replaced the original parent pathname with a symlink to an outside temporary directory. The repository's real `writeFileContent()` helper followed the new ancestor and created the file outside.

Static symlink rejection still worked when the outside link existed before validation.

## Consequence

The current boundary protects against path traversal and static symlink selection. It does not retain the ancestor directory authority observed during validation when a concurrent local actor can replace that ancestor before the final pathname syscall.

Final-component `wx` creation and sibling temporary-file rename do not pin ancestor identity.

## Governing invariant

A mutation described as limited to allowed directories should act through the same directory authority that was validated. Re-resolving mutable ancestors after validation must not silently widen the operation beyond the allowed roots.

## Exact source map

Pinned source: `modelcontextprotocol/servers@76d64c822f5125032f89eb71dbdb94e42b434821`.

- `src/filesystem/lib.ts::validatePath()` performs lexical and resolved-path checks.
- A nonexistent target validates the current real parent and returns the original absolute child pathname.
- `writeFileContent()` later calls `fs.writeFile(path, ..., { flag: "wx" })` or creates and renames a sibling temporary pathname.
- `src/filesystem/index.ts` uses the same validate-then-pathname pattern for create and move operations.
- MCP roots can replace the process-global allowed-directory set while the server remains active.

See `evidence/source-map.md` for the auditable source boundary.

## Exact execution receipt

Fieldwork executed head: `7bf4ac314f95b2d60c9383dd512191dcb0311f09`.

- target workflow `30650186407`, job `91221247782`: success;
- Fieldwork integrity `30650186303`: success;
- focused Fieldwork controls: 3/3;
- focused controls plus existing path-validation suite: 56/56;
- complete filesystem package: 8 files, 155 tests, all passed;
- TypeScript build: success;
- exact untracked-test carrier boundary: success;
- artifact `8801058697`;
- artifact digest `sha256:3f0c6a036fc449deae03f4382fcafb5c463a14b5172b434ae0c5f6e3cfcdab68`.

Detailed receipt: `evidence/linux-write-characterization.md`.

The temporary execution workflow is removed from the canonical head. The exact target test remains as durable evidence.

## Executed comparison

### Stable allowed parent

Validation plus the real write helper created the file inside the allowed root. No outside file appeared.

### Pre-existing outside symlink

Validation rejected the parent before mutation. No outside file appeared.

### Post-validation ancestor swap

Validation succeeded while the parent was a real allowed directory. After the deterministic swap, the real write helper created the asserted bytes in the outside directory. No file appeared under the parked inside parent.

## Repair families

### A — descriptor-relative ownership

Retain a directory capability and perform the final operation relative to it using an `openat` or `openat2`-style primitive. This best preserves the validated identity. Ordinary portable Node APIs do not expose a complete descriptor-relative filesystem surface.

### B — native or platform-specific helper

Introduce a small helper for descriptor-relative mutation and confinement flags. This can close the primitive gap on supported platforms, with packaging, portability, and maintenance cost.

### C — bounded revalidation

Revalidate immediately before and after mutation and fail or roll back on movement. This detects many changes but leaves a residual race between the final check and pathname syscall. It cannot support a claim of complete confinement against concurrent ancestor replacement.

### D — explicit threat-model boundary plus external sandboxing

State that allowed directories defend against request-path and static-symlink selection, while concurrent local namespace mutation requires an OS/container sandbox or stronger native primitive. This is the smallest truthful portable change, but it narrows the operator-facing meaning of “only works within allowed directories.”

## Current decision

The ancestor-identity gap is established for exact Linux write composition. A pure additional pathname recheck cannot restore the strong invariant, so it is rejected as a complete repair.

The next comparison is between:

1. a portable documentation/threat-model repair that names the residual local-actor boundary and recommends OS-level isolation; and
2. a platform-specific descriptor-relative proof showing whether a native helper can close the tested Linux case without changing ordinary callers.

Create-directory, move, and dynamic-root controls should be added only when they distinguish repair scope or authority semantics; they are no longer needed to prove the basic pathname race.

## Claim boundary

Established:

- exact Linux/Node nonexistent-file creation can escape the validated ancestor after a deterministic parent swap;
- static outside symlink rejection works for the tested pre-validation case;
- stable-parent ordinary behavior remains intact;
- full target package and build remain green with the characterization.

Not established:

- public exploitability, attacker reachability, production prevalence, or impact;
- MCP transport invocation of the tool handler;
- create-directory, move, edit, existing-file replacement, or roots-revocation behavior;
- Windows or macOS behavior;
- a portable complete repair;
- upstream acceptance.

## Exact next transition

Prepare two bounded candidates: one documentation-only threat-model patch and one Linux descriptor-relative feasibility probe. Apply the same criteria—truthful confinement claim, compatibility, portability, rollback, maintenance, and residual race—and choose autonomously from executed evidence.

No merge, release, deployment, credential, private-data access, spending, or public-upstream interaction is authorized.