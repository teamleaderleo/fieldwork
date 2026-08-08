# Node controls for Fieldwork #709

Execution environment:

- Node: `v22.16.0`
- bundled undici: `6.21.2`
- commands executed locally on 2026-08-08

Evidence class: `model-executed` / reference execution. These are Node controls, not Bun target execution.

## Request constructor

`node probes/request-constructor-node.mjs`

| Case | Result |
| --- | --- |
| URL + GET + body | `TypeError: Request with GET/HEAD method cannot have body.` |
| URL + HEAD + body | same |
| POST Request input + GET | same |
| POST Request input + HEAD | same |
| input + GET + overriding body | same |
| input + GET + `body: null` | same |
| input + GET + `body: undefined` | same |
| disturbed input + GET | GET/HEAD body error wins |
| disturbed input + POST | `TypeError: Cannot construct a Request with a Request object that has already been used.` |
| locked input + GET | GET/HEAD body error wins |
| locked input + POST | used-body error wins |
| malformed URL + GET + body | URL parsing error wins |
| GET + `ReadableStream` + `keepalive: true` | GET/HEAD body error wins |

The result agrees with Node's vendored undici constructor order: URL parsing occurs before method/body validation; the GET/HEAD body check occurs before body extraction and before the unusable-input-body check.

## Builtin specifier surfaces

`node probes/builtin-specifier-node.mjs`:

```text
import.meta.resolve("http")      -> "node:http"
import.meta.resolve("node:http") -> "node:http"
Module.isBuiltin("http")         -> true
Module.isBuiltin("node:http")    -> true
```

CommonJS control:

```text
require.resolve("http")      -> "http"
require.resolve("node:http") -> "node:http"
require("http") === require("node:http") -> true
```

Node loader hook control, with a module importing both spellings:

```text
HOOK "http"
HOOK "node:http"
```

This separates semantic identity from source-observer fidelity: Node canonicalizes `import.meta.resolve("http")`, while its loader hook and `require.resolve()` preserve the spelling presented by the caller.

Node 22.16.0 predates the `module.import` diagnostics behavior used as the direct oracle by RoboBun #32628; that PR compares against Node 26.3.0 for the diagnostics event itself.
