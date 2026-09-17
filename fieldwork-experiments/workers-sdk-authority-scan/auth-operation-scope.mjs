import assert from "node:assert/strict";

async function profileSwitchModel() {
	let activeProfile = "default";
	const tokenByProfile = new Map([
		["profile-A", "token-A"],
		["profile-B", "token-B"],
	]);
	const events = [];

	function setProfile(profile) {
		activeProfile = profile;
	}

	function requireApiToken() {
		return tokenByProfile.get(activeProfile);
	}

	let releaseA;
	const gate = new Promise((resolve) => {
		releaseA = resolve;
	});

	async function operationA() {
		events.push(`A:start:${requireApiToken()}`);
		await gate;
		events.push(`A:resume:${requireApiToken()}`);
	}

	setProfile("profile-A");
	const pendingA = operationA();
	setProfile("profile-B");
	releaseA();
	await pendingA;

	assert.deepEqual(events, ["A:start:token-A", "A:resume:token-B"]);
	console.log("PASS: pending operation switches to later active auth profile");
}

async function temporaryAccountModel() {
	let temporaryAllowed = false;
	let activeTemporaryAccount;
	const storedToken = "stored-token-A";

	function setTemporaryAllowed(allowed) {
		temporaryAllowed = allowed;
		activeTemporaryAccount = undefined;
	}

	function activateTemporaryAccount(account) {
		assert.equal(temporaryAllowed, true);
		activeTemporaryAccount = account;
	}

	function getAPIToken() {
		return activeTemporaryAccount?.token ?? storedToken;
	}

	let releaseA;
	const gate = new Promise((resolve) => {
		releaseA = resolve;
	});
	const observed = [];

	async function operationA() {
		observed.push(`A:start:${getAPIToken()}`);
		await gate;
		observed.push(`A:resume:${getAPIToken()}`);
	}

	setTemporaryAllowed(true);
	activateTemporaryAccount({ token: "temporary-token-A" });
	const pendingA = operationA();

	setTemporaryAllowed(false);
	releaseA();
	await pendingA;

	assert.deepEqual(observed, [
		"A:start:temporary-token-A",
		"A:resume:stored-token-A",
	]);
	console.log(
		"PASS: later command dispatch clears a pending operation's temporary account"
	);
}

async function explicitAuthContextModel() {
	const events = [];
	let releaseA;
	const gate = new Promise((resolve) => {
		releaseA = resolve;
	});

	async function operation(context) {
		events.push(`A:start:${context.token}`);
		await gate;
		events.push(`A:resume:${context.token}`);
	}

	const pending = operation({ profile: "profile-A", token: "token-A" });
	const laterContext = { profile: "profile-B", token: "token-B" };
	assert.equal(laterContext.token, "token-B");
	releaseA();
	await pending;

	assert.deepEqual(events, ["A:start:token-A", "A:resume:token-A"]);
	console.log("PASS: explicit auth context preserves operation credential ownership");
}

await profileSwitchModel();
await temporaryAccountModel();
await explicitAuthContextModel();
