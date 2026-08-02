import assert from "node:assert/strict";
import { AsyncLocalStorage } from "node:async_hooks";

async function cachedAccountValidationModel() {
	let credential = "credential-A";
	let cachedAccount = { id: "account-A", name: "A" };
	const accessible = {
		"credential-A": new Set(["account-A"]),
		"credential-B": new Set(["account-B"]),
		"credential-C": new Set(["account-A", "account-C"]),
	};
	const selectedByCredential = {
		"credential-A": { id: "account-A", name: "A" },
		"credential-B": { id: "account-B", name: "B" },
		"credential-C": { id: "account-C", name: "C" },
	};
	const validations = [];
	const selections = [];

	async function canAccessAccount(id) {
		validations.push([credential, id]);
		return accessible[credential].has(id);
	}

	async function selectAccount() {
		selections.push(credential);
		return selectedByCredential[credential];
	}

	async function getOrSelectAccountId(config = {}) {
		if (config.account_id) return config.account_id;
		if (config.env_account_id) return config.env_account_id;
		if (cachedAccount && (await canAccessAccount(cachedAccount.id))) {
			return cachedAccount.id;
		}
		const selected = await selectAccount();
		cachedAccount = selected;
		return selected.id;
	}

	assert.equal(await getOrSelectAccountId(), "account-A");
	credential = "credential-B";
	assert.equal(await getOrSelectAccountId(), "account-B");
	credential = "credential-C";
	assert.equal(await getOrSelectAccountId(), "account-C");
	assert.equal(
		await getOrSelectAccountId({ account_id: "explicit-config" }),
		"explicit-config"
	);
	assert.equal(
		await getOrSelectAccountId({ env_account_id: "explicit-env" }),
		"explicit-env"
	);
	assert.deepEqual(validations, [
		["credential-A", "account-A"],
		["credential-B", "account-A"],
		["credential-C", "account-B"],
	]);
	assert.deepEqual(selections, ["credential-B", "credential-C"]);
	console.log(
		"PASS: cached account is reused only after current-credential validation"
	);
	console.log(
		"PASS: explicit config and environment account IDs retain precedence"
	);
}

async function authOperationContextModel() {
	const authState = new AsyncLocalStorage();
	const fallback = {
		profile: "default",
		temporaryAllowed: false,
		temporaryAccount: undefined,
	};
	const tokens = new Map([
		["profile-A", "token-A"],
		["profile-B", "token-B"],
	]);

	function state() {
		return authState.getStore() ?? fallback;
	}

	function runAuthOperation(initial, callback) {
		return authState.run(
			{ ...initial, temporaryAccount: undefined },
			callback
		);
	}

	function activateTemporaryAccount(account) {
		const current = state();
		assert.equal(current.temporaryAllowed, true);
		current.temporaryAccount = account;
	}

	function requireApiToken() {
		const current = state();
		return current.temporaryAccount?.token ?? tokens.get(current.profile);
	}

	let releaseA;
	const gate = new Promise((resolve) => {
		releaseA = resolve;
	});
	const events = [];
	const pendingA = runAuthOperation(
		{ profile: "profile-A", temporaryAllowed: true },
		async () => {
			activateTemporaryAccount({ token: "temporary-A" });
			events.push(`A:start:${requireApiToken()}`);
			await gate;
			events.push(`A:resume:${requireApiToken()}`);
		}
	);
	const operationB = runAuthOperation(
		{ profile: "profile-B", temporaryAllowed: false },
		async () => {
			events.push(`B:${requireApiToken()}`);
		}
	);
	await operationB;
	releaseA();
	await pendingA;
	assert.deepEqual(events, [
		"A:start:temporary-A",
		"B:token-B",
		"A:resume:temporary-A",
	]);
	console.log(
		"PASS: async auth operation context preserves profile and temporary account"
	);
}

async function deployContextForwardingModel() {
	const operationContext = new AsyncLocalStorage();
	let fallbackContext;

	function initFallback(context) {
		fallbackContext = context;
	}

	function current() {
		const value = operationContext.getStore() ?? fallbackContext;
		if (!value) throw new Error("deploy helper context not initialized");
		return value;
	}

	function runWithDeployContext(context, callback) {
		return operationContext.run(context, callback);
	}

	const fetchResult = (...args) => current().fetchResult(...args);
	const logger = {
		log: (...args) => current().logger.log(...args),
	};

	const events = [];
	const contextA = {
		fetchResult: async (value) => `fetch-A:${value}`,
		logger: { log: (value) => events.push(`logger-A:${value}`) },
	};
	const contextB = {
		fetchResult: async (value) => `fetch-B:${value}`,
		logger: { log: (value) => events.push(`logger-B:${value}`) },
	};
	initFallback(contextB);
	let releaseA;
	const gate = new Promise((resolve) => {
		releaseA = resolve;
	});
	const pendingA = runWithDeployContext(contextA, async () => {
		logger.log("start");
		await gate;
		logger.log(await fetchResult("/resource-A"));
	});
	await runWithDeployContext(contextB, async () => {
		logger.log(await fetchResult("/resource-B"));
	});
	releaseA();
	await pendingA;
	assert.deepEqual(events, [
		"logger-A:start",
		"logger-B:fetch-B:/resource-B",
		"logger-A:fetch-A:/resource-A",
	]);
	console.log(
		"PASS: forwarding adapters preserve deploy-helper operation ownership"
	);
}

await cachedAccountValidationModel();
await authOperationContextModel();
await deployContextForwardingModel();
