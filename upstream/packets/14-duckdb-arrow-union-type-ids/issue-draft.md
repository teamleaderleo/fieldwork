# Private upstream issue draft

> Draft only. Public upstream contact requires explicit authorization.

## Title

Arrow sparse unions interpret logical type IDs as child indexes

## Body

DuckDB's Arrow sparse-union conversion appears to use each value in the union type-ID buffer as a positional child index. Arrow schemas can assign non-positional logical IDs in the supported `0..127` range, for example `+us:5,7,9`, where those IDs identify children zero, one, and two.

A focused characterization shows two related correctness problems:

1. non-positional logical IDs must be mapped through the schema's type-ID list before selecting a child and constructing the DuckDB union tag;
2. for a sparse union with a nonzero offset, the same effective offset must be supplied to the child conversions, or a correct logical tag can be paired with a value from the wrong physical row.

A candidate fix parses the schema type-ID list, stores a 128-entry ID-to-child-index map, resolves each runtime type ID through that map, writes the mapped child index as the DuckDB union tag, and forwards `array.offset + parent_offset` through child conversion.

The candidate also rejects malformed input explicitly:

- negative or above-range schema IDs;
- duplicate schema IDs;
- schema type-ID count mismatch;
- negative or unmapped runtime IDs.

Focused private controls cover identity, non-sequential, reordered, upper-bound, and offset cases. The offset fixture uses an unsliced three-row root containing a sparse-union child with offset one and length three over four physical entries.

Questions for maintainers if public contact is later authorized:

1. Is schema conversion the preferred location for range, duplicate, and count validation?
2. Is rejecting every negative or unmapped runtime ID the expected behavior, rather than coercing it to a positional index?
3. Should the effective sparse-union offset be passed uniformly through default, dictionary, and run-end child conversion paths?

Private evidence:

- characterization: `teamleaderleo/duckdb#12@ed05ac593498fb4f95546ec591824ee23429088d`;
- passing parent candidate: `teamleaderleo/duckdb#14@c962ece64c1356015aef15a37c0cc636f63b376b`;
- current repair carrier: `teamleaderleo/duckdb#16@c9938e6d637217d1cd4b41a739b2c179d97f6b2b`;
- target base: `2c9e51aa33dd07e928edae66304430aeb038edd7`;
- current focused run: `30929848690`;
- current Main run: `30929853935`;
- public defect reference, read-only: `duckdb/duckdb#21842`.

Current publication blocker: all native positive and malformed controls, artifact verification, and exact clean-branch publication must be green at the same carrier revision. No public write is authorized.
