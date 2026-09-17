// Fieldwork #709 reference control.
// Executed with Node v22.16.0 / undici 6.21.2.
// Run: node request-constructor-node.mjs

const cases = [];

function record(name, fn) {
  try {
    const value = fn();
    cases.push({ name, ok: true, value: value?.method ?? String(value) });
  } catch (error) {
    cases.push({ name, ok: false, error: error.name, message: error.message });
  }
}

const postRequest = () =>
  new Request("https://example.com/", { method: "POST", body: "payload" });

record("url-get-body", () =>
  new Request("https://example.com/", { method: "GET", body: "x" }),
);
record("url-head-body", () =>
  new Request("https://example.com/", { method: "HEAD", body: "x" }),
);
record("input-get", () => new Request(postRequest(), { method: "GET" }));
record("input-head", () => new Request(postRequest(), { method: "HEAD" }));
record("input-get-override", () =>
  new Request(postRequest(), { method: "GET", body: "override" }),
);
record("input-get-null", () =>
  new Request(postRequest(), { method: "GET", body: null }),
);
record("input-get-undefined", () =>
  new Request(postRequest(), { method: "GET", body: undefined }),
);

const disturbed = postRequest();
await disturbed.text();
record("disturbed-get", () => new Request(disturbed, { method: "GET" }));
record("disturbed-post", () => new Request(disturbed, { method: "POST" }));

const locked = postRequest();
const reader = locked.body.getReader();
record("locked-get", () => new Request(locked, { method: "GET" }));
record("locked-post", () => new Request(locked, { method: "POST" }));
reader.releaseLock();

record("invalid-url-get-body", () =>
  new Request("::::", { method: "GET", body: "x" }),
);
record("stream-get-keepalive", () =>
  new Request("https://example.com/", {
    method: "GET",
    body: new ReadableStream(),
    duplex: "half",
    keepalive: true,
  }),
);

console.log(
  JSON.stringify(
    { node: process.version, undici: process.versions.undici, cases },
    null,
    2,
  ),
);
