# F406 exact source map

Target: `modelcontextprotocol/servers@76d64c822f5125032f89eb71dbdb94e42b434821`  
Observed: 2026-07-31  
Evidence class: source-read  
Upstream contact authorized: no

## Validation boundary

`src/filesystem/lib.ts::validatePath(requestedPath)`:

1. expands home syntax;
2. resolves a lexical absolute pathname;
3. checks that lexical pathname against global allowed directories;
4. for an existing target, awaits `fs.realpath(absolute)` and checks the resolved result;
5. for `ENOENT`, awaits `fs.realpath(path.dirname(absolute))`, checks that parent, and returns the original absolute child pathname.

The returned authority token is a pathname string. No directory descriptor, inode identity, mount identity, or ancestor generation is retained.

## Mutation boundary

`src/filesystem/lib.ts::writeFileContent(filePath, content)`:

- first attempts `fs.writeFile(filePath, content, { flag: "wx" })`;
- on `EEXIST`, writes a sibling temporary pathname and calls `fs.rename(tempPath, filePath)`.

`wx` rejects an existing final path. It does not prevent the operating system from resolving a changed ancestor directory at the later syscall.

`src/filesystem/index.ts` also performs:

- `validatePath(path)` followed by `fs.mkdir(validPath, { recursive: true })`;
- separate source/destination validation followed by `fs.rename(validSourcePath, validDestPath)`;
- validation followed by read, edit, list, stat, and recursive search operations.

## Dynamic authority boundary

`updateAllowedDirectoriesFromRoots()` replaces the process-global allowed-directory list after an MCP roots update. `validatePath()` and later operations have no operation-scoped allowed-root generation or revocation check.

## Existing controls inspected

`src/filesystem/__tests__/path-validation.test.ts` covers:

- exact and nested allowed paths;
- common-prefix sibling rejection;
- traversal normalization;
- null bytes;
- static symlink support and platform behavior;
- Unicode and separator cases.

No inspected control swaps an ancestor after `validatePath()` returns and before the final mutation syscall.

## Prepared discriminator

The target-native test imports the exact exported functions:

- `setAllowedDirectories()`;
- `validatePath()`;
- `writeFileContent()`.

It validates a nonexistent child while its parent is a real allowed directory, then deterministically:

1. renames the validated parent aside;
2. creates a directory symlink at the original parent pathname pointing to an outside temporary directory;
3. invokes `writeFileContent()` with the already-validated child pathname;
4. checks inside and outside locations;
5. removes the complete temporary root.

The stable-parent and pre-existing-outside-symlink cases are retained as positive and negative controls.