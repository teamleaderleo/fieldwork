# Pull-request draft — Unit 02

Status: `DRAFT FOR HUMAN EDITING`  
Public interaction authorized: `no`

## Proposed title

`fix: make relocatable launchers compatible with BusyBox realpath`

## Draft body

Closes X

### Summary

Since BusyBox `realpath` treats `--` as a pathname, uv-generated relocatable launchers can still run on Alpine while printing:

```text
realpath: --: No such file or directory
```

I propose removing `--` from the generated `realpath` calls. We can leave `dirname --` as-is, which leaves quoting and symlink resolution unchanged.

`uv run` also needs to recognize both the updated and existing launcher forms so launchers created by older uv versions keep working.

A helper or parser may make sense as a later cleanup, but keeping the four known forms explicit keeps this fix small and easy to review.

### Test plan

- Updated the wheel and relocatable-venv expectations.
- Added coverage for the current and legacy `python` and `python3` launcher forms.
- Ran formatting, compilation, Clippy, and GNU, BusyBox, and macOS shell checks.

## Internal note

Replace `X` with the issue number before submission. No public upstream action has been taken.
