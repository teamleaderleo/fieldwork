import { expect, test } from "bun:test";

// Prepared compatibility regression for the synchronous literal-IP connect
// failure left out of oven-sh/bun#37093.
//
// The destination is a live loopback listener so the remote endpoint itself is
// valid. `1.2.3.4` is the invalid local bind address used by Node's vendored
// test-http-localaddress-bind-error.js. On a normal host the bind fails before
// the connect can become asynchronous, which currently loses the errno and
// rejects as generic FailedToOpenSocket.
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

  // Some synchronous-failure implementations may not enter the callback path.
  // If it does fire, it must carry the same error fidelity as the promise.
  if (callbackError !== undefined) {
    expect(callbackError.code).toBe("EADDRNOTAVAIL");
    expect(callbackError.syscall).toBe("connect");
  }
});
