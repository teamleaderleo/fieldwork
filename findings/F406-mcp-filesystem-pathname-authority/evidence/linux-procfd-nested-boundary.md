# F406 Linux procfd nested-component boundary

State: `primitive-executed-local`  
Assistance ID: `assist-fieldwork-406-procfd-nested-boundary-01`  
Owning issue: `teamleaderleo/fieldwork#406`  
Parent primitive: `teamleaderleo/fieldwork#409@b398f38185296248a671054f58d36076c41683df`  
Executed helper generation: `teamleaderleo/fieldwork#415@ed73ceef5e92a158b61d41ff77eb2c9421f9251f`  
Target source context: `modelcontextprotocol/servers@76d64c822f5125032f89eb71dbdb94e42b434821`  
Upstream contact authorized: no

## Question

Does opening only the top validated parent retain authority over a later unresolved nested component, or must the immediate mutation parent itself be opened before the namespace can change?

## Why this discriminator matters

PR #409 proves direct-child creation and sibling-temp replacement through `/proc/self/fd/<opened-parent-fd>/...`. A target API may receive nested relative paths. Resolving unresolved components beneath the top procfd root still asks the kernel to traverse their current namespace entries.

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

Observed result: the write landed outside. Opening an ancestor did not pin the unresolved descendant.

### Immediate-parent descriptor positive control

- open `allowed/pivot/nested` before the swap;
- rename that nested directory aside and install the outside symlink;
- write through `/proc/self/fd/<nested-fd>/inside.txt`;
- require the bytes under the parked, opened inside directory and no outside file.

Observed result: the write remained inside the parked directory represented by the open descriptor.

## Exact execution receipt

Focused workflow run `30652868492`, attempt `1`, job `91230119938` completed successfully at literal helper head `ed73ceef5e92a158b61d41ff77eb2c9421f9251f`.

Environment:

- Ubuntu 24.04 hosted runner;
- Node `v22.23.1`;
- mounted `/proc/self/fd`;
- no credentials and no hosted target request.

Results:

- `top-parent procfd still follows a swapped unresolved nested component`: passed;
- `pre-opened immediate nested parent retains authority after nested swap`: passed;
- total: 2 tests, 2 passed, 0 failed, 0 skipped.

Artifact:

- ID `8802596465`;
- name `fieldwork-406-procfd-nested-30652868492-1`;
- server digest `sha256:028da7d030815cd39345cfd3bc55f3aeeb20e875d9b5656a820e7c2ac56deb87`;
- retained files: exact TAP output and schema-1 JSON receipt;
- expiry: 2026-08-14.

Evidence class: `primitive-executed-local`. The generic Fieldwork integrity run on the later workflow-free generation is a separate repository gate and does not change this focused primitive result.

## Technical consequence

A Linux hardened path cannot safely open only the allowed root or another high ancestor and then append an arbitrary unresolved relative path. For each mutation it must resolve and retain the exact immediate parent directory capability, with every preceding component traversed under a fail-closed no-symlink or equivalent identity-retaining policy.

Node's ordinary high-level filesystem API does not expose `openat2()` resolution flags. Procfd can express final operations relative to an opened immediate parent, but safely obtaining that parent for a nested path remains a separate design problem. A native helper, component-by-component descriptor walk, or a clearly weaker documented fallback may be required.

The same boundary applies to path-based directory-mtime mutation in `teamleaderleo/linux-fieldwork#384`: protecting only the final component is insufficient when an ancestor can be replaced before descendant resolution.

## Claim boundary

The experiment is limited to Linux, mounted procfs, Node 22, temporary directories, one nested component, exclusive file creation, and directory symlink replacement by a concurrent local actor.

It does not establish a target patch, safe component-by-component traversal, `openat2()` availability, create-directory or cross-parent move semantics, procfs-unavailable behavior, descriptor cleanup under target exceptions, macOS, Windows, exploitability, prevalence, production impact, or upstream acceptance.

## Transition

The disposable workflow is removed from the helper branch after evidence transfer. Retain the test and this note as the reviewable evidence package. The next technical comparison should evaluate safe acquisition of an exact nested immediate parent, including ancestor replacement, device boundaries, descriptor cleanup, and an explicit portability/fallback policy.

No merge, release, deployment, credentials, private-data access, spending, writer transfer, or public-upstream interaction is included or authorized.
