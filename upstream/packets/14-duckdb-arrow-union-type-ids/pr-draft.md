# Private upstream pull-request draft

> Draft only. Public upstream contact requires explicit authorization.

## Title

fix(arrow): map sparse union type IDs to child indices

## Summary

Arrow sparse-union type IDs are logical schema codes and may differ from positional child indexes. Parse the schema's type-code list, retain a logical-ID to child-index mapping, and use the mapped child index during conversion.

## Proposed source scope

- add union-specific Arrow type information containing children and the ID map;
- parse and validate sparse-union type codes from the Arrow schema;
- resolve type-ID buffer values through the map;
- preserve correct reads for sliced parent arrays;
- reject unknown, out-of-range, and duplicate logical IDs;
- keep the diff free of Fieldwork carrier files and unrelated formatting changes.

## Tests

- sparse IDs `{3,7}` select children `{0,1}`;
- parent offsets `1` and `2` preserve tag and value selection;
- duplicate type codes are rejected;
- malformed type-ID storage is rejected after the hardening behavior is repaired and verified.

## Evidence

- characterization head: `ed05ac593498fb4f95546ec591824ee23429088d`;
- passing minimal candidate head: `c962ece64c1356015aef15a37c0cc636f63b376b`;
- hardening head: `fa8cb6605b6aa7865d85f8010b6fd57fbd3512b2`;
- intended clean base: `2c9e51aa33dd07e928edae66304430aeb038edd7`.

## Pre-publication checklist

- [ ] diagnose targeted hardening run `30659465467`;
- [ ] materialize source on `fix/arrow-sparse-union-type-id-map`;
- [ ] remove five formatting-only paths from the generated patch;
- [ ] commit focused tests as normal target source;
- [ ] run targeted debug test and relevant DuckDB test suite;
- [ ] run formatting/lint checks;
- [ ] update exact source head and test links in this packet;
- [ ] obtain explicit authorization before any public write.