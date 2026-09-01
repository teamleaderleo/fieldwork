import assert from "node:assert/strict";

async function staleServiceHeaderModel() {
	const headersCache = {};
	const usesAccessCache = new Map([["protected.example", true]]);
	let clientId = "client-A";
	let clientSecret = "secret-A";

	async function domainUsesAccess(domain) {
		return usesAccessCache.get(domain) ?? false;
	}

	async function getAccessHeaders(domain) {
		if (clientId && clientSecret) {
			const headers = {
				"CF-Access-Client-Id": clientId,
				"CF-Access-Client-Secret": clientSecret,
			};
			headersCache[domain] = headers;
			return headers;
		}
		if (!(await domainUsesAccess(domain))) return {};
		if (headersCache[domain]) return headersCache[domain];
		throw new Error("Access credentials required");
	}

	assert.deepEqual(await getAccessHeaders("protected.example"), {
		"CF-Access-Client-Id": "client-A",
		"CF-Access-Client-Secret": "secret-A",
	});
	clientId = undefined;
	clientSecret = undefined;
	assert.deepEqual(await getAccessHeaders("protected.example"), {
		"CF-Access-Client-Id": "client-A",
		"CF-Access-Client-Secret": "secret-A",
	});
	console.log(
		"PASS: removed Access service credentials still reuse the cached prior headers"
	);
}

async function partialCredentialModel() {
	const headersCache = {};
	let clientId = "client-A";
	let clientSecret = "secret-A";
	async function getAccessHeaders(domain) {
		if (clientId && clientSecret) {
			return (headersCache[domain] = {
				"CF-Access-Client-Id": clientId,
				"CF-Access-Client-Secret": clientSecret,
			});
		}
		if (headersCache[domain]) return headersCache[domain];
		throw new Error("Access credentials required");
	}
	await getAccessHeaders("protected.example");
	clientSecret = undefined;
	assert.deepEqual(await getAccessHeaders("protected.example"), {
		"CF-Access-Client-Id": "client-A",
		"CF-Access-Client-Secret": "secret-A",
	});
	console.log(
		"PASS: a partial current Access credential pair can fall back to the complete cached prior pair"
	);
}

async function stickyNegativeDetectionModel() {
	const usesAccessCache = new Map();
	let probeResult = "error";
	let probes = 0;
	async function domainUsesAccess(domain) {
		if (usesAccessCache.has(domain)) return usesAccessCache.get(domain);
		probes++;
		if (probeResult === "error") {
			usesAccessCache.set(domain, false);
			return false;
		}
		usesAccessCache.set(domain, probeResult === "access");
		return usesAccessCache.get(domain);
	}
	assert.equal(await domainUsesAccess("protected.example"), false);
	probeResult = "access";
	assert.equal(await domainUsesAccess("protected.example"), false);
	assert.equal(probes, 1);
	console.log(
		"PASS: a transient Access detection failure becomes a process-lifetime negative result"
	);
}

async function ownerScopedRepairModel() {
	function getServiceHeaders(current) {
		if (!current.clientId || !current.clientSecret) {
			throw new Error("Access credentials required");
		}
		return {
			"CF-Access-Client-Id": current.clientId,
			"CF-Access-Client-Secret": current.clientSecret,
		};
	}
	assert.deepEqual(
		getServiceHeaders({ clientId: "client-B", clientSecret: "secret-B" }),
		{
			"CF-Access-Client-Id": "client-B",
			"CF-Access-Client-Secret": "secret-B",
		}
	);
	assert.throws(() => getServiceHeaders({}), /credentials required/);
	console.log(
		"PASS: per-call service headers cannot outlive the current credential pair"
	);
}

await staleServiceHeaderModel();
await partialCredentialModel();
await stickyNegativeDetectionModel();
await ownerScopedRepairModel();
