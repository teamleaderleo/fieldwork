import assert from "node:assert/strict";
import {
	existsSync,
	mkdtempSync,
	mkdirSync,
	rmSync,
	writeFileSync,
} from "node:fs";
import os from "node:os";
import path from "node:path";

// Source-pinned model of the discovery order at
// cloudflare/workers-sdk@69ef8228fd96b4df192195d93c33e56ae665500a:
//
// - Wrangler/workers-utils searches upward and prefers
//   wrangler.json -> wrangler.jsonc -> wrangler.toml.
// - @cloudflare/vite-plugin scans only the Vite root and prefers
//   wrangler.jsonc -> wrangler.json -> wrangler.toml.

function findUp(fileName, startDirectory) {
	let directory = path.resolve(startDirectory);
	while (true) {
		const candidate = path.join(directory, fileName);
		if (existsSync(candidate)) {
			return candidate;
		}

		const parent = path.dirname(directory);
		if (parent === directory) {
			return undefined;
		}
		directory = parent;
	}
}

function wranglerDiscovery(startDirectory) {
	return (
		findUp("wrangler.json", startDirectory) ??
		findUp("wrangler.jsonc", startDirectory) ??
		findUp("wrangler.toml", startDirectory)
	);
}

function viteDiscovery(root) {
	for (const extension of ["jsonc", "json", "toml"]) {
		const candidate = path.join(root, `wrangler.${extension}`);
		if (existsSync(candidate)) {
			return candidate;
		}
	}
	return undefined;
}

function createFile(filePath) {
	mkdirSync(path.dirname(filePath), { recursive: true });
	writeFileSync(filePath, "{}\n", "utf8");
}

function runScenario({ name, root, startDirectory = root, files, expected }) {
	for (const relativePath of files) {
		createFile(path.join(root, relativePath));
	}

	const wrangler = wranglerDiscovery(startDirectory);
	const vite = viteDiscovery(startDirectory);
	const actual = {
		wrangler: wrangler ? path.relative(root, wrangler) : undefined,
		vite: vite ? path.relative(root, vite) : undefined,
		sameSelection: wrangler === vite,
	};

	assert.deepEqual(actual, expected, `Unexpected result for scenario: ${name}`);
	return { name, ...actual };
}

const temporaryRoot = mkdtempSync(path.join(os.tmpdir(), "workers-config-discovery-"));

try {
	const results = [];

	const dualFormatRoot = path.join(temporaryRoot, "dual-format");
	results.push(
		runScenario({
			name: "same root with wrangler.json and wrangler.jsonc",
			root: dualFormatRoot,
			files: ["wrangler.json", "wrangler.jsonc"],
			expected: {
				wrangler: "wrangler.json",
				vite: "wrangler.jsonc",
				sameSelection: false,
			},
		})
	);

	const nestedRoot = path.join(temporaryRoot, "nested-root");
	const nestedApplication = path.join(nestedRoot, "apps", "dashboard");
	mkdirSync(nestedApplication, { recursive: true });
	results.push(
		runScenario({
			name: "nested Vite root with parent wrangler.jsonc",
			root: nestedRoot,
			startDirectory: nestedApplication,
			files: ["wrangler.jsonc"],
			expected: {
				wrangler: "wrangler.jsonc",
				vite: undefined,
				sameSelection: false,
			},
		})
	);

	const tomlRoot = path.join(temporaryRoot, "toml-control");
	results.push(
		runScenario({
			name: "same root with only wrangler.toml",
			root: tomlRoot,
			files: ["wrangler.toml"],
			expected: {
				wrangler: "wrangler.toml",
				vite: "wrangler.toml",
				sameSelection: true,
			},
		})
	);

	console.log(JSON.stringify(results, null, 2));
} finally {
	rmSync(temporaryRoot, { recursive: true, force: true });
}
