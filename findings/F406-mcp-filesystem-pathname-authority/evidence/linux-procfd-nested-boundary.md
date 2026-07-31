# F406 Linux procfd nested-component boundary

State: `execution-carrier-prepared`  
Assistance ID: `assist-fieldwork-406-procfd-nested-boundary-01`  
Owning issue: `teamleaderleo/fieldwork#406`  
Parent primitive: `teamleaderleo/fieldwork#409@b398f38185296248a671054f58d36076c41683df`  
Target source context: `modelcontextprotocol/servers@76d64c822f5125032f89eb71dbdb94e42b434821`  
Upstream contact authorized: no

## Question

Does opening only the top validated parent retain authority over a later unresolved nested component, or must the immediate mutation parent itself be opened before the namespace can change?

## Why this discriminator matters

PR #409 proves direct-child creation and sibling-temp replacement through `/proc/self/fd/<opened-parent-fd>/...`. A target API may receive nested relative paths. Resolving those unresolved components beneath the top procfd root still asks the kernel to traverse their current namespace entries.

A nested directory can therefore be renamed and replaced with an outside-pointing symlink after the top parent is opened. The experiment distinguishes:

1. a top-parent descriptor followed by unresolved `nested/file` traversal; and
2. an immediate nested-parent descriptor opened before the nested pathname is replaced.

## Exact controls

### Top-parent descriptor negative control

- create `allowed/pivot/nested` and an outside directory;
- open `allowed/pivot` with `O_RDONLY | O_DIRECTORY`;
- rename `nested` aside and install a symlink at the old nested pathname pointing outside;
- write through `/proc/self/fd/<pivot-fd>/nested/escaped.txt`;
- require the bytes to appear outside and no file under the parked inside nested directory.

This is the expected reversing result: opening an ancestor does not pin unresolved descendants.

### Immediate-parent descriptor positive control

- open `allowed/pivot/nested` before the swap;
- rename that nested directory aside and install the outside symlink;
- write through `/proc/self/fd/<nested-fd>/inside.txt`;
- require the bytes under the parked, opened inside directory and no outside file.

## Provisional technical consequence

A Linux hardened path cannot safely open only the allowed root or another high ancestor and then append an arbitrary unresolved relative path. For each mutation it must resolve and retain the exact immediate parent directory capability, with every preceding component traversed under a fail-closed no-symlink or equivalent identity-retaining policy.

Node's ordinary high-level filesystem API does not expose `openat2()` resolution flags. Procfd can express final operations relative to an opened immediate parent, but safely obtaining that parent for a nested path remains a separate design problem. A native helper, component-by-component descriptor walk, or a clearly weaker documented fallback may be required.

## Claim boundary

The experiment is limited to Linux, mounted procfs, Node 22, temporary directories, one nested component, exclusive file creation, and directory symlink replacement by a concurrent local actor.

It does not establish a target patch, safe component-by-component traversal, `openat2()` availability, create-directory or cross-parent move semantics, procfs-unavailable behavior, descriptor cleanup under target exceptions, macOS, Windows, exploitability, prevalence, production impact, or upstream acceptance.

## Execution gate

Run `.github/workflows/fieldwork-406-procfd-nested-boundary.yml` at the literal helper head. Inspect the TAP output and JSON artifact before moving this record to `primitive-executed-local`.

No merge, release, deployment, credentials, private-data access, spending, writer transfer, or public-upstream interaction is included or authorized.
