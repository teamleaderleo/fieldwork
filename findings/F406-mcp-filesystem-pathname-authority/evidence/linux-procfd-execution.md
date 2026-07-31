# F406 Linux procfd authority execution receipt

Evidence class: `primitive-executed-local`  
Fieldwork executed head: `1ecdca9770c7780fe9de2c226f6e4c1850ae6679`  
Canonical finding: PR #408  
Target source context: `modelcontextprotocol/servers@76d64c822f5125032f89eb71dbdb94e42b434821`  
Environment: Ubuntu 24.04, Linux, Node 22.23.1  
Target source mutation: none  
Hosted request: no  
Credentials or private data: no

## Exact workflow

- run: `30650666819`;
- job: `91222837286`;
- result: success;
- prepared-head Fieldwork integrity: `30650666774`, success;
- artifact: `8801230952`;
- artifact digest: `sha256:20ee6dfb106439da7e8fbedc8cc89012c0d12b48de1b6c61fb1dcf241acc4239`.

Every workflow phase passed:

- literal Fieldwork head checkout;
- exact target-context checkout;
- Linux, `/proc/self/fd`, and Node identity checks;
- three primitive controls;
- untouched target worktree;
- exact receipt assembly and upload.

## Executed controls

Node's built-in test runner reported 3/3 passed.

### Ordinary pathname baseline

After the inside parent pathname was renamed aside and replaced with a directory symlink to the outside temporary directory, an ordinary pathname `writeFile(..., { flag: "wx" })` followed the replacement ancestor. The asserted bytes appeared outside and no file appeared under the parked inside parent.

### Opened-directory child creation

The test opened the inside parent with `O_RDONLY | O_DIRECTORY`, retained that `FileHandle`, then addressed the child through:

```text
/proc/self/fd/<directory-fd>/created.txt
```

After the original parent pathname was renamed aside and replaced by the outside symlink, the write created the file under the renamed, opened inside directory. The outside directory remained untouched.

### Opened-directory sibling temp and rename

The test opened the parent, created a sibling temporary file through the procfd directory, and renamed that temporary file over an existing child through the same procfd root after the pathname swap.

The replacement occurred under the renamed, opened inside parent. Neither the destination nor the temporary file appeared outside.

## Technical conclusion

On the executed Linux/Node environment, an open directory descriptor plus `/proc/self/fd/<fd>/...` retains the directory object across rename and pathname replacement for:

- exclusive child creation; and
- sibling temporary-file creation plus rename replacement.

This closes the exact ancestor-swap primitive demonstrated by the F406 write characterization without a compiled native addon.

## Limits

This result requires:

- Linux;
- mounted and usable procfs;
- `O_DIRECTORY` support;
- permission to open and retain the parent directory;
- an operation lifetime that bounds descriptor ownership and cleanup.

It does not establish:

- a complete target patch or public API;
- nested unresolved child-path confinement;
- create-directory, move, edit, or roots-revocation semantics;
- behavior in containers without procfs;
- macOS or Windows behavior;
- packaging or upstream acceptance;
- public exploitability or production prevalence.

## Workflow retirement

The execution workflow is temporary. The workflow-free generation retains this receipt, the exact Node control, and the feasibility record. Primitive claims remain bound to executed head `1ecdca9770c7780fe9de2c226f6e4c1850ae6679`, run `30650666819`, and the exact environment above.