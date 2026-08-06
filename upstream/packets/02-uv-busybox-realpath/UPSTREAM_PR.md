# Pull-request record — Unit 02

Status: `CLOSED WITHOUT MERGE`  
Public interaction: complete

Public pull request: [astral-sh/uv#20943](https://redirect.github.com/astral-sh/uv/pull/20943)

## Submitted title

`Make relocatable launchers compatible with BusyBox realpath`

## Evolution of the submitted approach

### Initial submission

The first public candidate removed `--` only from generated `realpath` calls while retaining `dirname --`, quoting, symlink canonicalization, and current/historical launcher recognition.

Maintainer review rejected that form because a bare entrypoint name beginning with `-` could be reinterpreted as an option on implementations that support ordinary option parsing.

### Revised submission

The PR was reworked around a runtime capability probe. It preserved `realpath -- "$0"` when `realpath -- /` succeeded and returned `/`, and used the BusyBox-compatible form otherwise.

The revised patch added:

- fake compliant and BusyBox-style `realpath` test executables;
- a bare `-foo` operand control;
- a literal file named `--` control;
- current and historical `python` / `python3` launcher recognition;
- POSIX and Fish activation updates.

Final public head: `28b00fc950c7eb924ab243418d44ce16ac5bee5a`  
Final canonical CI: run `31059965759` — success  
Final diff: four files, 207 additions, 16 deletions

## Review outcome

uv maintainers clarified that runtime probing was not an acceptable downstream tradeoff because of its per-launcher runtime cost and generated-shell complexity. The PR was closed without merge.

The preferred direction moved upstream to BusyBox: [vda-linux/busybox_mirror#26](https://redirect.github.com/vda-linux/busybox_mirror/issues/26).

This was not a correctness or CI rejection of the final patch. It was a project-level choice about where the compatibility responsibility should live.

## Communication closeout

The public thread included a detailed explanation of explored alternatives. The useful process lesson is to keep that exploration in the packet, lead maintainer discussion with the most relevant finding, and ask a narrow architectural question before implementing an ambiguous requested direction.

The target project's AI policy was surfaced during closeout. Future packets for that project must require the contributor to write final maintainer-facing text directly in their own words.

## Final rule

Do not reopen this PR or submit a replacement downstream probe unless uv maintainers explicitly request a new downstream approach.
