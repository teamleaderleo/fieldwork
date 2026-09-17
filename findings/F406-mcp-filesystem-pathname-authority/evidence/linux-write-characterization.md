# F406 Linux write characterization receipt

Evidence class: `target-executed-local`  
Fieldwork executed head: `7bf4ac314f95b2d60c9383dd512191dcb0311f09`  
Target: `modelcontextprotocol/servers@76d64c822f5125032f89eb71dbdb94e42b434821`  
Target package: `@modelcontextprotocol/server-filesystem` `0.6.3`  
Environment: Ubuntu 24.04, Node 22.23.1, npm 10.9.8  
Hosted request: no  
Credentials or private data: no

## Exact workflow

- run: `30650186407`;
- job: `91221247782`;
- result: success;
- artifact: `8801058697`;
- artifact digest: `sha256:3f0c6a036fc449deae03f4382fcafb5c463a14b5172b434ae0c5f6e3cfcdab68`;
- Fieldwork integrity: `30650186303`, success.

Every named workflow phase succeeded:

- literal Fieldwork head checkout;
- exact target checkout;
- committed dependency installation;
- focused controls;
- complete filesystem package tests;
- TypeScript build;
- exact untracked-test carrier boundary;
- receipt assembly and upload.

## Focused result

`fieldwork-pathname-authority.test.ts`: 3/3 passed.

Combined with the repository's existing path-validation suite: 56/56 passed across two files.

### Stable parent

Validation and the real `writeFileContent()` helper created `created.txt` inside the allowed root. No file appeared in the outside control directory.

### Pre-existing outside symlink

Validation rejected a parent that already resolved to the outside control directory. No outside file appeared.

### Post-validation ancestor swap

The test:

1. created an ordinary parent inside the allowed root;
2. validated a nonexistent child through the repository's real `validatePath()`;
3. renamed the validated parent aside;
4. installed a directory symlink at the original parent pathname pointing to the outside control directory;
5. invoked the repository's real `writeFileContent()` with the already-validated pathname.

The write succeeded. The asserted bytes appeared in the outside directory, and no file appeared under the parked inside parent.

This establishes that final-component `wx` creation does not retain the ancestor directory authority observed by `validatePath()`.

## Complete package result

The complete filesystem package passed:

- 8 test files;
- 155 tests;
- repository path, library, roots, directory-tree, structured-content, startup, and Fieldwork controls;
- coverage collection;
- package TypeScript build.

The target worktree remained unchanged except for the one copied untracked Fieldwork test.

## Claim boundary

Established for exact Linux/Node source:

- nonexistent-file creation through `validatePath()` plus `writeFileContent()` can follow an ancestor symlink installed after validation;
- static symlink rejection remains effective for the tested pre-validation case;
- stable-parent ordinary behavior remains intact.

Not executed or claimed:

- MCP transport invocation of the tool handler;
- create-directory, move, edit, or existing-file replacement races;
- dynamic roots revocation;
- another operating system;
- an external attacker model, production prevalence, or impact;
- repair compatibility or upstream acceptance.

## Workflow retirement

The execution workflow is temporary. The canonical next head removes it while retaining this report, the exact test, source map, and finding. Target claims remain bound to executed head `7bf4ac314f95b2d60c9383dd512191dcb0311f09` and the identities above.