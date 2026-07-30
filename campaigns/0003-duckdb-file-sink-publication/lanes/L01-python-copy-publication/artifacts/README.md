# L01 Artifact Index

Campaign: #55  
Lane: `L01-python-copy-publication`  
Upstream contact authorized: `false`

## Final successful run

- DuckDB fork head: `teamleaderleo/duckdb@d9d14e7f1d51694237029354ef637b0806878290`
- Workflow run: `30472702522`
- Conclusion: `success`
- Artifact ID: `8732359343`
- Artifact name: `fieldwork-issue55-results-v5`
- Artifact digest: `sha256:162b10cfa7cc5fbb7b360b02836d236592de55aeb4cd2728298fa86117a8a02d`
- Runner: Ubuntu 24.04, Linux 6.17 Azure x86_64
- Python: 3.13.14
- DuckDB package: 1.5.5
- Wheel SHA-256: `078e6a60dd8eedde5832f45422ca5c4a6b8c837aeabd8a56ca0b7d933f588053`

The workflow artifact contains the unabridged JSON:

- `issue55-results-v2.json` — 42/42 checks passed;
- `issue55-crash-threshold.json` — 18/18 checks passed;
- `issue55-tmp-publication-v2.json` — 58/58 checks passed.

## Durable compact results

- `results/issue55-broad-matrix.compact.json`
- `results/issue55-crash-threshold.compact.json`
- `results/issue55-tmp-publication.compact.json`

The compact copies retain all case observations needed for the report while removing repeated per-check detail blocks. The unabridged workflow files had these SHA-256 values:

- broad matrix: `457a24f9132279ec3e6b474a8fb805b8fdc80231119fba22f41aea2b6443c611`
- exact crash threshold: `7d507be6fb4acd1a02047416e6d4479224db4b42f855aa7745b0345befd77870`
- temporary publication: `6d9fd8d8e9429b0593e882039dfd698f912e2256042c24d4a3c2e5c600dbe351`

## Probe code

The owned DuckDB fork PR is backlink-suppressed here:

https://redirect.github.com/teamleaderleo/duckdb/pull/1

Files at the final head:

- `tools/fieldwork/issue55_file_sink_probe.py`
- `tools/fieldwork/issue55_file_sink_probe_v2.py`
- `tools/fieldwork/issue55_crash_threshold_probe.py`
- `tools/fieldwork/issue55_tmp_publication_probe.py`
- `tools/fieldwork/issue55_tmp_publication_probe_v2.py`
- `tools/fieldwork/requirements-issue55.txt`
- `.github/workflows/fieldwork-issue55-file-sink.yml`

## Retained failed hypotheses

### Initial retry expectation

The first run expected crash residue to block a same-path retry. It passed 30 of 32 checks; both failures showed that retry succeeded. The branch retains that probe.

- Run: `30471438784`
- Artifact: `8731798602`
- Digest: `sha256:dfcff197148b55331c49372866ddff5a2396fdec0a88f1a67b97cae0a428369c`

### Broad crash placement correction

The first corrected broad matrix waited a fixed 30 seconds before process kill. Its format result was valid, but its stated one-MiB placement was not. The exact-threshold probe replaced that control.

### Client-return marker expectation

The first temporary publication matrix required the final path to remain absent until a marker written after Python `execute()` returned. It passed 44 of 46 checks; both failures showed final publication immediately before the marker. The corrected probe inspected the file at first sighting and found exact content.

- Run: `30472408836`
- Artifact: `8732246682`
- Digest: `sha256:f6b908f5b58380ca9b643b23528ba5017bf3abaa2023761dcd11f18934a34564`

These failures are part of the evidence history and are described in the lane report.
