# Node controls for Fieldwork #709

Execution environment:

- Node: `v22.16.0`
- bundled undici: `6.21.2`
- original commands executed locally on 2026-08-08
- Request precedence matrix re-executed and extended on 2026-08-09

Evidence class: `model-executed` / reference execution. These are Node controls, not Bun target execution.

## Request constructor

Original retained probe: `node probes/request-constructor-node.mjs`.

Refined precedence probe re-ran the multi-invalid cases while promoting this candidate for presentation.

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
| GET + `ReadableStream` + `keepalive: true` | GET/HEAD body error wins |
| POST + `ReadableStream` + `keepalive: true` | `TypeError: keepalive` |
| malformed URL + GET + string body | URL parsing error wins |
| malformed URL + GET + `ReadableStream` + `keepalive: true` | URL parsing error wins |

Exact refined output:

```text
GET init string body: TypeError: Request with GET/HEAD method cannot have body.
GET inherited body: TypeError: Request with GET/HEAD method cannot have body.
HEAD init string body: TypeError: Request with GET/HEAD method cannot have body.
HEAD inherited body: TypeError: Request with GET/HEAD method cannot have body.
GET disturbed inherited body: TypeError: Request with GET/HEAD method cannot have body.
POST disturbed inherited body: TypeError: Cannot construct a Request with a Request object that has already been used.
GET locked inherited body: TypeError: Request with GET/HEAD method cannot have body.
POST locked inherited body: TypeError: Cannot construct a Request with a Request object that has already been used.
GET stream+keepalive: TypeError: Request with GET/HEAD method cannot have body.
POST stream+keepalive: TypeError: keepalive
bad URL + GET string body: TypeError: Failed to parse URL from ::::
bad URL + GET stream+keepalive: TypeError: Failed to parse URL from ::::
GET inherited + body null: TypeError: Request with GET/HEAD method cannot have body.
GET inherited + body undefined: TypeError: Request with GET/HEAD method cannot have body.
GET inherited + body fresh: TypeError: Request with GET/HEAD method cannot have body.
```

The result agrees with Node's vendored undici constructor order: RequestInit conversion happens first; a string input URL is parsed before the constructor body phase; final method selection happens before the GET/HEAD-body check; the GET/HEAD body check happens before body extraction and before the unusable-input-body check.

A Proxy control also confirmed Node's RequestInit converter reads members before URL parsing. This is useful when reviewing an implementation: the target fix should preserve WebIDL member conversion side effects while moving **body extraction/materialization**, not blindly move every init property read behind URL parsing.

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
