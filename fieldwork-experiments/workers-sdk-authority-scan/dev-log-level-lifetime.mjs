import assert from "node:assert/strict";
import { AsyncLocalStorage } from "node:async_hooks";

async function failedStartModel() {
	const logger = { level: "log" };
	async function startDev(logLevel) {
		if (logLevel) logger.level = logLevel;
		throw new Error("sentinel startup failure");
	}
	await assert.rejects(startDev("error"), /startup failure/);
	assert.equal(logger.level, "error");
	console.log("PASS: failed dev startup leaves the singleton logger overridden");
}

async function successfulStopModel() {
	const logger = { level: "log" };
	async function startDev(logLevel) {
		if (logLevel) logger.level = logLevel;
		return { stop: async () => {} };
	}
	const dev = await startDev("debug");
	await dev.stop();
	assert.equal(logger.level, "debug");
	console.log("PASS: successful dev stop leaves the singleton logger overridden");
}

async function overlappingDevModel() {
	const logger = { level: "log" };
	const events = [];
	async function dev(owner, level, gate) {
		logger.level = level;
		events.push(`${owner}:start:${logger.level}`);
		await gate;
		events.push(`${owner}:resume:${logger.level}`);
	}
	let releaseA;
	const gateA = new Promise((resolve) => {
		releaseA = resolve;
	});
	const pendingA = dev("A", "debug", gateA);
	await dev("B", "error", Promise.resolve());
	releaseA();
	await pendingA;
	assert.deepEqual(events, [
		"A:start:debug",
		"B:start:error",
		"B:resume:error",
		"A:resume:error",
	]);
	console.log("PASS: overlapping dev sessions replace each other's log level");
}

async function asyncLogContextModel() {
	const logContext = new AsyncLocalStorage();
	const fallback = "log";
	const events = [];
	const level = () => logContext.getStore() ?? fallback;
	let releaseA;
	const gateA = new Promise((resolve) => {
		releaseA = resolve;
	});
	const pendingA = logContext.run("debug", async () => {
		events.push(`A:start:${level()}`);
		await gateA;
		events.push(`A:resume:${level()}`);
	});
	await logContext.run("error", async () => {
		events.push(`B:${level()}`);
	});
	releaseA();
	await pendingA;
	assert.deepEqual(events, ["A:start:debug", "B:error", "A:resume:debug"]);
	console.log("PASS: async-local log levels preserve concurrent owner intent");
}

await failedStartModel();
await successfulStopModel();
await overlappingDevModel();
await asyncLogContextModel();
