# Batches

Each batch is a bounded dispatch set with one parent issue and one durable directory.

Use the identifier form `BYYYYMMDD-NNN-slug`.

Required files:

- `manifest.json`
- `STATUS.md`
- `results/<assignment-id>.md`
- `synthesis.md`
- `closeout.md`

The coordinator owns shared files. Workers own only their assigned result paths.

Start from:

- `templates/batch-manifest.json`
- `templates/batch-result.md`
- `templates/batch-synthesis.md`
- `BATCHES.md`
