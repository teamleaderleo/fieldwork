import assert from "node:assert/strict";

async function accountCacheModel() {
	let currentCredential = "credential-A";
	let cachedAccount;
	const accountFetches = [];
	const accountsByCredential = {
		"credential-A": [{ id: "account-A", name: "A" }],
		"credential-B": [{ id: "account-B", name: "B" }],
	};

	async function fetchAllAccounts() {
		accountFetches.push(currentCredential);
		return accountsByCredential[currentCredential];
	}

	function getActiveAccountId(config = {}) {
		return (
			config.account_id ??
			process.env.CLOUDFLARE_ACCOUNT_ID ??
			cachedAccount?.id
		);
	}

	async function getOrSelectAccountId(config = {}) {
		const activeAccountId = getActiveAccountId(config);
		if (activeAccountId) return activeAccountId;

		const accounts = await fetchAllAccounts();
		if (accounts.length === 1) {
			cachedAccount = accounts[0];
			return accounts[0].id;
		}
		throw new Error("Unexpected account matrix");
	}

	assert.equal(await getOrSelectAccountId(), "account-A");
	currentCredential = "credential-B";
	assert.equal(await getOrSelectAccountId(), "account-A");
	assert.deepEqual(accountFetches, ["credential-A"]);
	console.log(
		"PASS: credential change reuses prior cached account without account lookup"
	);

	const accountCacheByProfile = new Map([
		["default", { id: "account-public" }],
	]);
	const laterComplianceRegion = "fedramp";
	assert.equal(accountCacheByProfile.get("default")?.id, "account-public");
	assert.equal(laterComplianceRegion, "fedramp");
	console.log(
		"PASS: profile-only cache does not encode compliance or API environment"
	);
}

async function deployContextModel() {
	let fetchResult;
	let logger;
	const events = [];

	function initDeployHelpersContext(context) {
		fetchResult = context.fetchResult;
		logger = context.logger;
	}

	let releaseOperationA;
	const operationAGate = new Promise((resolve) => {
		releaseOperationA = resolve;
	});

	async function operationA() {
		logger("A:start");
		await operationAGate;
		const value = await fetchResult("/accounts/A/workers");
		logger(`A:result:${value}`);
	}

	initDeployHelpersContext({
		logger: (message) => events.push(`logger-A:${message}`),
		fetchResult: async (url) => `fetch-A:${url}`,
	});
	const pendingA = operationA();

	initDeployHelpersContext({
		logger: (message) => events.push(`logger-B:${message}`),
		fetchResult: async (url) => `fetch-B:${url}`,
	});
	releaseOperationA();
	await pendingA;

	assert.deepEqual(events, [
		"logger-A:A:start",
		"logger-B:A:result:fetch-B:/accounts/A/workers",
	]);
	console.log(
		"PASS: pending operation switches to later global fetch and logger context"
	);

	async function operationWithExplicitContext(context, gate) {
		context.logger("A:start");
		await gate;
		const value = await context.fetchResult("/accounts/A/workers");
		context.logger(`A:result:${value}`);
	}

	const isolatedEvents = [];
	let releaseExplicitOperation;
	const explicitGate = new Promise((resolve) => {
		releaseExplicitOperation = resolve;
	});
	const explicitOperation = operationWithExplicitContext(
		{
			logger: (message) => isolatedEvents.push(`logger-A:${message}`),
			fetchResult: async (url) => `fetch-A:${url}`,
		},
		explicitGate
	);

	initDeployHelpersContext({
		logger: (message) => isolatedEvents.push(`logger-B:${message}`),
		fetchResult: async (url) => `fetch-B:${url}`,
	});
	releaseExplicitOperation();
	await explicitOperation;

	assert.deepEqual(isolatedEvents, [
		"logger-A:A:start",
		"logger-A:A:result:fetch-A:/accounts/A/workers",
	]);
	console.log(
		"PASS: explicit operation context keeps fetch and logger ownership stable"
	);
}

await accountCacheModel();
await deployContextModel();
