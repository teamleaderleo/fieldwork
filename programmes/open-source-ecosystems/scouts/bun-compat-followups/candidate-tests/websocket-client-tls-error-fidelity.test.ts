import { expect, test } from "bun:test";
import { expiredTls, tls as validTls } from "harness";
import { once } from "node:events";
import net from "node:net";

// Fieldwork-owned candidate regression for the WebSocket sibling follow-up
// explicitly deferred by oven-sh/bun#36149.
// Evidence: target-test-prepared. This file has NOT been executed on Bun.

const mismatchedClientTls = {
  cert: validTls.cert,
  key: expiredTls.key,
  rejectUnauthorized: false,
};

function waitForFailure(ws: WebSocket) {
  return new Promise<{ error: ErrorEvent; close: CloseEvent; errorCount: number }>((resolve, reject) => {
    let errorEvent: ErrorEvent | undefined;
    let errorCount = 0;
    ws.onopen = () => reject(new Error("WebSocket unexpectedly opened"));
    ws.onerror = event => {
      errorCount++;
      errorEvent = event as ErrorEvent;
    };
    ws.onclose = event => {
      if (!errorEvent) return reject(new Error("WebSocket closed without an error event"));
      resolve({ error: errorEvent, close: event, errorCount });
    };
  });
}

test("direct wss client TLS setup exposes ERR_OSSL_X509_KEY_VALUES_MISMATCH", async () => {
  using server = Bun.serve({
    port: 0,
    hostname: "127.0.0.1",
    tls: validTls,
    fetch(req, server) {
      if (server.upgrade(req)) return;
      return new Response("upgrade failed", { status: 500 });
    },
    websocket: {
      message() {},
    },
  });

  const ws = new WebSocket(`wss://127.0.0.1:${server.port}`, {
    tls: mismatchedClientTls,
  });
  const { error, close, errorCount } = await waitForFailure(ws);

  expect(errorCount).toBe(1);
  expect(error.error).toBeInstanceOf(Error);
  expect((error.error as any).code).toBe("ERR_OSSL_X509_KEY_VALUES_MISMATCH");
  // Diagnostic fidelity must not change WebSocket lifecycle policy.
  expect(close.code).toBe(1006);
  expect(close.wasClean).toBe(false);
});

test("wss through HTTP CONNECT proxy exposes the same TLS setup code", async () => {
  // The target only provides a real URL/port. The TLS context build fails after
  // the proxy's 200 response, before encrypted tunnel traffic is needed.
  using target = Bun.serve({
    port: 0,
    hostname: "127.0.0.1",
    tls: validTls,
    fetch(req, server) {
      if (server.upgrade(req)) return;
      return new Response("upgrade failed", { status: 500 });
    },
    websocket: {
      message() {},
    },
  });

  const proxy = net.createServer(client => {
    client.on("error", () => {});
    client.once("data", () => {
      client.write("HTTP/1.1 200 Connection established\r\n\r\n");
    });
  });
  proxy.listen(0, "127.0.0.1");
  await once(proxy, "listening");
  const proxyPort = (proxy.address() as net.AddressInfo).port;

  try {
    const ws = new WebSocket(`wss://127.0.0.1:${target.port}`, {
      proxy: `http://127.0.0.1:${proxyPort}`,
      tls: mismatchedClientTls,
    });
    const { error, close, errorCount } = await waitForFailure(ws);

    expect(errorCount).toBe(1);
    expect(error.error).toBeInstanceOf(Error);
    expect((error.error as any).code).toBe("ERR_OSSL_X509_KEY_VALUES_MISMATCH");
    expect(close.code).toBe(1006);
    expect(close.wasClean).toBe(false);
  } finally {
    proxy.close();
  }
});
