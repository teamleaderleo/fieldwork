# F406 Linux procfd feasibility comparison

State: `primitive-executed`  
Evidence class: `primitive-executed-local`  
Canonical finding: PR #408  
Target source context: `modelcontextprotocol/servers@76d64c822f5125032f89eb71dbdb94e42b434821`  
Platform: Linux only  
Upstream contact authorized: no

## Question

Can ordinary Node 22 on Linux retain an opened parent-directory capability through a rename and pathname replacement strongly enough to prevent the exact outside-write result established by F406, without a compiled native addon?

## Candidate primitive

Open the validated parent directory with `O_RDONLY | O_DIRECTORY`, retain the `FileHandle`, and address final children through:

```text
/proc/self/fd/<directory-fd>/<child>
```

Linux resolves the procfd link through the opened directory object. The executed test determines whether that identity survives when the original parent pathname is renamed aside and replaced by an outside-pointing symlink.

## Exact execution

- Fieldwork head: `1ecdca9770c7780fe9de2c226f6e4c1850ae6679`;
- workflow `30650666819`, job `91222837286`: success;
- prepared-head Fieldwork integrity `30650666774`: success;
- Node controls: 3/3 passed;
- target-context worktree: untouched;
- artifact `8801230952`;
- artifact digest `sha256:20ee6dfb106439da7e8fbedc8cc89012c0d12b48de1b6c61fb1dcf241acc4239`.

Detailed receipt: `linux-procfd-execution.md`.

## Results

1. **Ordinary pathname baseline:** followed the swapped ancestor and wrote outside.
2. **Opened-directory child creation:** wrote under the renamed, opened inside parent and left outside untouched.
3. **Opened-directory sibling temp and rename:** replaced the existing file under the renamed, opened inside parent and left outside untouched.

Every reversing outcome was avoided in the executed Ubuntu 24.04 / Node 22.23.1 environment. The directory handle remained usable after rename, both mutation forms retained the opened parent, and cleanup closed the handle and removed the complete temporary root.

## Decision criteria result

- closes the exact executed Linux ancestor-swap primitive: **yes**;
- uses available Node 22 primitives without a compiled addon: **yes**;
- retains final-component `wx` and sibling-temp rename mechanics: **yes in the executed controls**;
- portable beyond Linux with mounted procfs: **no**;
- fallback behavior when procfs or `O_DIRECTORY` is unavailable: **not designed**;
- operation-scoped descriptor lifetime: **mechanically demonstrated**;
- complete target repair or cross-platform confinement: **not established**.

## Technical selection

Retain this as the leading Linux hardening primitive. It is stronger than repeated pathname revalidation for the exact ancestor-swap case because the mutation resolves through an already-open directory object.

It does not replace the portable threat-model repair. The best-supported direction is layered:

1. document the current concurrent-local-namespace limitation and require OS/container isolation where strong confinement is expected;
2. evaluate an optional Linux hardened mutation path using an opened parent plus procfd;
3. fail closed or use explicitly documented ordinary-path behavior when the Linux primitive is unavailable—never silently label the fallback as race-complete confinement.

## Remaining target discriminators

Before preparing a target source candidate, execute:

- nested child-path handling where more than one unresolved component remains;
- behavior when the opened parent is deleted or its mount changes;
- procfs unavailable or inaccessible;
- operation-scoped handle closure on success and every failure path;
- existing-file replacement through the target's exact helper composition;
- API shape that keeps ordinary callers compatible and makes the Linux-only guarantee observable.

Create-directory, cross-parent move, recursive edit/search, dynamic roots, macOS, and Windows remain separately scoped.

## Claim boundary

A green primitive result establishes Linux feasibility only. It does not establish public exploitability, production prevalence, complete MCP filesystem confinement, target acceptance, or portability.