# F406 Linux procfd feasibility comparison

State: `target-test-prepared`  
Evidence class: `primitive-execution-prepared`  
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

Linux resolves the procfd link through the opened directory object. The test determines whether that identity survives when the original parent pathname is renamed aside and replaced by an outside-pointing symlink.

## Controls

1. ordinary pathname baseline follows the swapped ancestor and writes outside;
2. procfd child creation writes under the renamed, opened parent and leaves outside untouched;
3. procfd sibling temporary-file creation plus rename replaces an existing file under the opened parent and leaves outside untouched.

All paths are disposable temporary directories. The test performs no MCP request, source mutation, credential use, or external filesystem access.

## Decision criteria

- closes the exact executed Linux ancestor-swap case;
- uses available Node 22 primitives;
- retains current final-component `wx` and sibling-temp semantics;
- does not claim portability beyond Linux with mounted `/proc`;
- names behavior when `/proc`, `O_DIRECTORY`, or permissions are unavailable;
- keeps the opened directory handle lifetime bounded to one operation;
- does not turn a Linux feasibility result into a complete cross-platform repair claim.

## Reversing outcomes

Reject this primitive if:

- procfd creation follows the replacement symlink;
- sibling temp/rename crosses outside or fails under ordinary ext4 runner semantics;
- the opened directory cannot be used after rename;
- cleanup or descriptor lifetime is ambiguous.

A green result establishes Linux feasibility only. It does not settle API design, other operations, containers without procfs, macOS, Windows, packaging, or target acceptance.