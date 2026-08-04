# Research lane — `arrow_scan` repeatability and single-consumer semantics

Date: 2026-08-05

## Status

`OPEN CORRECTNESS GAP — current PR incomplete/stale, generic design unresolved`

This note is read-only research. It does not modify or contact public upstream.

## Two distinct failure classes

### Explicit multiple references

Open `duckdb/duckdb-python#70` demonstrates a query that references one registered Arrow stream twice:

```sql
SELECT id FROM arrow_stream
UNION ALL
SELECT id + 1 FROM arrow_stream;
```

Observed behavior differs by client:

- Java: the second scan fails because the stream has been released;
- Python: the query completes but returns only the first scan's rows, which is silent incorrect output;
- explicitly materializing the stream into a DuckDB table first produces the correct result.

This is a clear user-visible contract gap: a one-shot stream is being treated as a repeatable relation without an explicit capability boundary.

### Optimizer-introduced duplication

Open `duckdb/duckdb-java#713` is more serious as a regression. A query contains only one Arrow table reference, but DuckDB 1.5's window self-join optimization rewrites the plan into multiple Arrow scans. The user cannot avoid the failure merely by following a “reference streams once” rule.

Open core PR `duckdb/duckdb#23323` proposes `TableFunction.supports_multiple_scans = false` and makes the window self-join optimizer decline the rewrite. The PR itself notes that CTE inlining can duplicate the same upstream subtree and is not covered.

A maintainer comment suggests a generic future solution: detect multiple scans and materialize the source as a CTE. No replacement implementation or timeline was found.

## Current code boundary

`arrow_scan` receives:

- an opaque factory pointer;
- a producer callback returning an `ArrowArrayStreamWrapper`;
- a schema callback.

At global initialization it calls the producer to obtain a stream. Whether that producer is repeatable depends on the client binding:

- a factory may create a fresh stream each time;
- a registered Arrow stream may wrap one consumable object whose release is final;
- a relation/table object may be restartable;
- a generator/reader may be logically one-shot even if its wrapper survives.

`TableFunctionParallelism::SEQUENTIAL` describes concurrent consumption of one scan. It does not describe whether the table function may be instantiated or executed more than once.

## Design choices

### Option A — table-function repeatability capability

Add an explicit capability such as `supports_multiple_scans` or a richer enum.

Pros:

- generic and visible to optimizers;
- useful beyond Arrow streams;
- can prevent unsafe plan duplication early.

Cons:

- every optimizer that copies/scans subtrees must honor it;
- equality, serialization, C API, extensions, and planner transforms may need updates;
- a boolean may be too weak because some factories are repeatable and some are not.

### Option B — bind/factory-specific capability

Let `ArrowScanFunctionData` or the producer callback report repeatability.

Pros:

- accurately distinguishes a PyArrow table from a one-shot stream;
- confines policy to Arrow scan integration.

Cons:

- optimizers need access to bind-data capabilities;
- pointer callback ABI changes may affect clients;
- plan serialization/deep copy still needs a generic representation.

### Option C — automatic materialization when duplication is required

When an optimizer or binder detects multiple references to a non-repeatable source, execute it once into a temporary/materialized relation.

Pros:

- preserves relational semantics and user expectations;
- centralizes the workaround;
- matches the manual workaround proven in issue #70.

Cons:

- memory/disk cost;
- pushdown and scheduling choices become important;
- materialization must happen once and be shared by every duplicated branch;
- error handling and lifetime across prepared statements need care.

### Option D — narrow rewrite/serialization guards

Disable specific transformations or make `arrow_scan` non-serializable.

Pros:

- small regression fix;
- could address window self-join quickly.

Cons:

- incomplete by construction;
- new optimizers can reintroduce duplication;
- explicit multiple references still fail or return wrong results;
- behavior remains client-dependent.

## Recommended direction

Treat repeatability as a relational source capability, not an Arrow-only quirk.

A practical staged approach:

1. add a narrow regression guard for optimizer-introduced duplication so one-reference queries do not regress;
2. define a generic repeatability/materialization contract for table functions;
3. let Arrow bindings report whether their factory can create independent streams;
4. materialize non-repeatable sources when the logical plan genuinely requires multiple scans;
5. retain projection/filter pushdown into the one physical source scan before materialization where safe.

## Discriminating tests

### Binding/factory variants

- restartable PyArrow table/dataset factory;
- one-shot PyArrow RecordBatchReader;
- Java ArrowArrayStream;
- C API stream factory that deliberately counts producer calls;
- producer that errors on second invocation;
- producer that returns independent streams.

### Plan shapes

1. explicit `UNION ALL` with two references;
2. self-join;
3. scalar and correlated subqueries;
4. CTE referenced twice, materialized and non-materialized forms;
5. window query whose optimizer currently introduces a self-join;
6. CTE inlining and common-subexpression rewrites;
7. repeated execution of a prepared statement;
8. concurrent queries against the same registered source;
9. LIMIT/filter/projection pushdown before required materialization;
10. early consumer cancellation and exception cleanup.

### Required assertions

- correct row set, not merely absence of error;
- exact producer invocation count;
- exact stream release count;
- no second read of a released one-shot stream;
- repeatable factories remain unmaterialized when unnecessary;
- optimizer-on and optimizer-off results agree.

## Interaction with unit 14

Unit 14's ownership-safe test stream exposed the same general lesson: copying or reusing Arrow C stream structs requires an explicit ownership/repeatability model. This lane is separate from union conversion correctness and should not be folded into the nine-file unit 14 source.

## Source links

- explicit multi-scan issue: `duckdb/duckdb-python#70`
- optimizer regression: `duckdb/duckdb-java#713`
- open partial core fix: `duckdb/duckdb#23323`
- current Arrow scanner: `src/function/table/arrow.cpp` at `daa81697e31a3dc97a93f11220037cd2213af6cd`
