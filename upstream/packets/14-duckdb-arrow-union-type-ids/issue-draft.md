# Private upstream issue draft

> Draft only. Public upstream contact requires explicit authorization.

## Title

Arrow sparse unions interpret signed logical type IDs as child indexes

## Body

DuckDB's Arrow sparse-union conversion appears to use each signed `int8_t` value in the union type-ID buffer as a positional child index. Arrow schemas can assign arbitrary signed logical IDs, for example `+us:-128,0,127`, where those IDs identify children zero, one, and two.

A focused characterization shows two related correctness problems:

1. non-positional logical IDs must be mapped through the schema's type-ID list before selecting a child and constructing the DuckDB union tag;
2. for a sparse union with a nonzero offset, the same effective offset must be supplied to the child conversions, or a correct logical tag can be paired with a value from the wrong physical row.

A candidate fix parses the signed schema type-ID list, stores a 256-entry ID-to-child-index map keyed by each ID's unsigned-byte representation, resolves each runtime type ID through that map, writes the mapped child index as the DuckDB union tag, and forwards `array.offset + parent_offset` through child conversion.

The candidate also rejects malformed input explicitly:

- duplicate positive or negative schema IDs;
- schema type-ID count mismatch;
- unmapped positive or negative runtime IDs.

Focused private controls cover identity, non-sequential, reordered, signed-boundary, and offset cases. The offset fixture uses an unsliced three-row root containing a sparse-union child with offset one and length three over four physical entries.

Questions for maintainers if public contact is later authorized:

1. Is schema conversion the preferred location for duplicate and count validation?
2. Is rejecting every unmapped runtime signed ID the expected behavior, rather than coercing it to a positional index?
3. Should the effective sparse-union offset be passed uniformly through default, dictionary, and run-end child conversion paths?

Private evidence:

- characterization: `teamleaderleo/duckdb#12@ed05ac593498fb4f95546ec591824ee23429088d`;
- passing parent candidate: `teamleaderleo/duckdb#14@c962ece64c1356015aef15a37c0cc636f63b376b`;
- current repair carrier: `teamleaderleo/duckdb#16@6ff47e3abad0e9412926b6b2dfd33ebb7b18ee2c`;
- target base: `2c9e51aa33dd07e928edae66304430aeb038edd7`;
- ordinary Main `30845355047`: success;
- focused native hardening `30845351615`, job `91792186958`: in progress;
- public defect reference, read-only: `duckdb/duckdb#21842`.

Current publication blocker: all native positive and malformed controls, artifact verification, and exact clean-branch publication must be green at the same carrier revision. No public write is authorized.
