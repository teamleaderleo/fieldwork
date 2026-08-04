# Pull-request draft — Unit 02

Status: `DRAFT FOR HUMAN EDITING`  
Public interaction authorized: `no`

## Proposed title

`fix: make relocatable launchers compatible with BusyBox realpath`

## Draft body

Closes X

## Summary

Since BusyBox `realpath` treats `--` as a pathname, uv-generated relocatable launchers can still run on Alpine while printing:

```text
realpath: --: No such file or directory
```

I propose removing `--` from the generated `realpath` calls. We can leave `dirname --` as-is, which leaves quoting and symlink resolution unchanged.

The launcher passes its own path through `$0`, so even a hyphenated filename is received as a path such as `./-tool` rather than a bare option.

`uv run` also reads these generated launchers, so I added four constants for the current and previous `python` and `python3` forms. That keeps launchers created by older uv versions working without adding a broader parser to this fix.

## Test Plan

- Updated the wheel and relocatable-venv expectations.
- Added coverage for the current and legacy `python` and `python3` launcher forms.
- Ran formatting, compilation, Clippy, and GNU, BusyBox, and macOS shell checks.

## Internal note

Replace `X` with the issue number before submission. No public upstream action has been taken.
