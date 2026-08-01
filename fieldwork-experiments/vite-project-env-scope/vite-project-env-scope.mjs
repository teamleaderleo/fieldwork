import assert from "node:assert/strict";

const PREFIXES = [
	"CLOUDFLARE_",
	"WRANGLER_HYPERDRIVE_LOCAL_CONNECTION_STRING_",
];

function loadEnvLikeVite(parsed, processEnv) {
	const env = {};
	for (const [key, value] of Object.entries(parsed)) {
		if (PREFIXES.some((prefix) => key.startsWith(prefix))) env[key] = value;
	}
	for (const [key, value] of Object.entries(processEnv)) {
		if (PREFIXES.some((prefix) => key.startsWith(prefix))) env[key] = value;
	}
	return env;
}

function currentResolve(parsed, processEnv) {
	const prefixedEnv = loadEnvLikeVite(parsed, processEnv);
	Object.assign(processEnv, prefixedEnv);
	return prefixedEnv;
}

function authLikeWorkersSdk(env) {
	if (env.CLOUDFLARE_API_KEY && env.CLOUDFLARE_EMAIL) {
		return {
			kind: "global-key",
			key: env.CLOUDFLARE_API_KEY,
			email: env.CLOUDFLARE_EMAIL,
		};
	}
	if (env.CLOUDFLARE_API_TOKEN) {
		return { kind: "token", token: env.CLOUDFLARE_API_TOKEN };
	}
	return undefined;
}

function explicitResolve(parsed, hostEnv) {
	const operationEnv = loadEnvLikeVite(parsed, hostEnv);
	return { operationEnv, hostEnv };
}

{
	const processEnv = {};
	const a = currentResolve({ CLOUDFLARE_API_TOKEN: "token-a" }, processEnv);
	const b = currentResolve({ CLOUDFLARE_API_TOKEN: "token-b" }, processEnv);
	assert.equal(a.CLOUDFLARE_API_TOKEN, "token-a");
	assert.equal(b.CLOUDFLARE_API_TOKEN, "token-a");
	assert.equal(processEnv.CLOUDFLARE_API_TOKEN, "token-a");
	console.log(
		"PASS: project A token overrides project B env file after process pollution"
	);
}

{
	const processEnv = {};
	currentResolve({ CLOUDFLARE_API_TOKEN: "token-a" }, processEnv);
	const b = currentResolve({}, processEnv);
	assert.equal(b.CLOUDFLARE_API_TOKEN, "token-a");
	console.log("PASS: project B with no token inherits project A token");
}

{
	const processEnv = {};
	currentResolve(
		{
			CLOUDFLARE_API_KEY: "key-a",
			CLOUDFLARE_EMAIL: "a@example.invalid",
		},
		processEnv
	);
	const b = currentResolve({ CLOUDFLARE_API_TOKEN: "token-b" }, processEnv);
	assert.deepEqual(authLikeWorkersSdk(b), {
		kind: "global-key",
		key: "key-a",
		email: "a@example.invalid",
	});
	console.log("PASS: inherited global key/email outranks project B token");
}

{
	const processEnv = {};
	currentResolve(
		{
			WRANGLER_HYPERDRIVE_LOCAL_CONNECTION_STRING_DB:
				"postgres://owner-a.invalid/db",
			CLOUDFLARE_VITE_FORCE_LOCAL: "true",
		},
		processEnv
	);
	const b = currentResolve({}, processEnv);
	assert.equal(
		b.WRANGLER_HYPERDRIVE_LOCAL_CONNECTION_STRING_DB,
		"postgres://owner-a.invalid/db"
	);
	assert.equal(b.CLOUDFLARE_VITE_FORCE_LOCAL, "true");
	console.log("PASS: connection and mode values persist into a later project");
}

{
	const hostEnv = {};
	const a = explicitResolve({ CLOUDFLARE_API_TOKEN: "token-a" }, hostEnv);
	const b = explicitResolve({ CLOUDFLARE_API_TOKEN: "token-b" }, hostEnv);
	assert.equal(a.operationEnv.CLOUDFLARE_API_TOKEN, "token-a");
	assert.equal(b.operationEnv.CLOUDFLARE_API_TOKEN, "token-b");
	assert.deepEqual(hostEnv, {});
	console.log(
		"PASS: explicit operation environments isolate owners and preserve host state"
	);
}

{
	const processEnv = {};
	const loadedA = loadEnvLikeVite(
		{ CLOUDFLARE_API_TOKEN: "token-a" },
		processEnv
	);
	const loadedB = loadEnvLikeVite(
		{ CLOUDFLARE_API_TOKEN: "token-b" },
		processEnv
	);
	Object.assign(processEnv, loadedA);
	Object.assign(processEnv, loadedB);
	assert.equal(processEnv.CLOUDFLARE_API_TOKEN, "token-b");
	assert.equal(loadedA.CLOUDFLARE_API_TOKEN, "token-a");
	assert.equal(loadedB.CLOUDFLARE_API_TOKEN, "token-b");
	assert.notEqual(
		processEnv.CLOUDFLARE_API_TOKEN,
		loadedA.CLOUDFLARE_API_TOKEN
	);
	console.log(
		"PASS: concurrent load/assign phases leave asynchronous owner A observing owner B global state"
	);
}
