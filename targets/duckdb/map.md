# Target Map: DuckDB

Repository: https://redirect.github.com/duckdb/duckdb

## In simple words

An embedded analytical database whose query engine, storage, extensions, file formats, and client boundaries can be exercised directly inside real applications without operating a separate database server.

## Areas worth understanding

- query planning and execution boundaries;
- transactions, interruption, and rollback;
- storage and file lifecycle;
- extensions and version compatibility;
- import, export, and schema evolution;
- memory and spill behavior;
- concurrency and connection ownership;
- client-language integration.

## Evidence we can produce

- deterministic datasets and queries;
- interruption and recovery tests;
- storage and file-corruption fixtures;
- compatibility matrices;
- realistic trials in Narrative DuckDB and BSC Compare;
- performance and memory baselines.

## Entry standard

State the exact DuckDB build, client, storage format, and dataset. Separate query-engine behavior from client-library or application behavior.

## Stop conditions

- the result depends on private or unshareable data;
- a benchmark lacks a stable baseline and workload;
- the behavior is only application SQL misuse;
- a broad optimizer rewrite is proposed before a bounded failure or opportunity is established.
