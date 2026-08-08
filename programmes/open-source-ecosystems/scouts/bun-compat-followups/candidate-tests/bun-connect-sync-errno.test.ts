import { expect, test } from "bun:test";

// Fieldwork-owned coverage candidate for oven-sh/bun#37093.
// Evidence: target-test-prepared. This file has NOT been executed on Bun.
//
// #37093's current head appears to have absorbed the synchronous local-bind
// errno fix even though its PR description still calls this a remaining gap.
// This test is therefore coverage material, not evidence of an independent
// implementation still being needed.
//
// The destination is a live loopback listener so the remote endpoint itself is
// valid. `1.2.3.4` is the invalid local bind address used by Node's vendored
// test-http-localaddress-bind-error.js. On a normal host the local bind should
// fail with EADDRNOTAVAIL before an asynchronous connect is established.
test("Bun.connect preserves EADDRNOTAVAIL from a synchronous local bind failure", async () => {
  using server = Bun.listen({
    hostname: "127.0.0.1",
    port: 0,
    socket: {
      data() {},
    },
  });

  let callbackError: any;
  const err = await Bun.connect({
    hostname: "127.0.0.1",
    port: server.port,
    localAddress: "1.2.3.4",
    socket: {
      data() {},
      connectError(_socket, error) {
        callbackError = error;
      },
    },
  }).then(
    () => {
      throw new Error("Bun.connect unexpectedly succeeded");
    },
    error => error,
  );

  expect(err).toBeInstanceOf(Error);
  expect(err.code).toBe("EADDRNOTAVAIL");
  expect(err.syscall).toBe("connect");
  expect(err.message).toBe("Failed to connect");
  expect(err.code).not.toBe("FailedToOpenSocket");

  if (callbackError !== undefined) {
    expect(callbackError.code).toBe("EADDRNOTAVAIL");
    expect(callbackError.syscall).toBe("connect");
  }
});
