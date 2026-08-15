#!/usr/bin/env node

import fs from "node:fs";
import path from "node:path";
import process from "node:process";

const root = process.cwd();
const entriesDir = path.join(root, "compendium", "entries");

const allowedKinds = new Set([
  "bug-species",
  "invariant",
  "hunting-technique",
  "repair-pattern",
  "regression-pattern",
  "concept",
  "anti-pattern",
  "executable-graduation",
]);
const allowedMaturity = new Set(["candidate", "supported", "mature"]);
const allowedFacetFamilies = new Set([
  "domains",
  "concerns",
  "mechanisms",
  "triggers",
  "techniques",
]);

function die(message) {
  console.error(message);
  process.exitCode = 1;
}

function loadEntries() {
  if (!fs.existsSync(entriesDir)) {
    throw new Error(`missing compendium entries directory: ${entriesDir}`);
  }

  return fs
    .readdirSync(entriesDir)
    .filter((name) => name.endsWith(".md"))
    .sort()
    .map((name) => {
      const file = path.join(entriesDir, name);
      const text = fs.readFileSync(file, "utf8");
      const match = text.match(/## Metadata\s*\n\s*```json\s*\n([\s\S]*?)\n```/);
      if (!match) {
        return { file, name, text, metadata: null, parseError: "missing metadata JSON block" };
      }

      try {
        return { file, name, text, metadata: JSON.parse(match[1]), parseError: null };
      } catch (error) {
        return { file, name, text, metadata: null, parseError: `invalid metadata JSON: ${error.message}` };
      }
    });
}

function validate(entries) {
  const errors = [];
  const byId = new Map();

  for (const entry of entries) {
    if (entry.parseError) {
      errors.push(`${entry.name}: ${entry.parseError}`);
      continue;
    }

    const metadata = entry.metadata;
    const expectedId = entry.name.replace(/\.md$/, "");

    if (metadata.schema !== 1) errors.push(`${entry.name}: schema must be 1`);
    if (metadata.id !== expectedId) errors.push(`${entry.name}: id must match filename (${expectedId})`);
    if (!/^[a-z0-9]+(?:-[a-z0-9]+)*$/.test(metadata.id ?? "")) {
      errors.push(`${entry.name}: id must be lowercase kebab-case`);
    }
    if (!allowedKinds.has(metadata.kind)) errors.push(`${entry.name}: unknown kind ${JSON.stringify(metadata.kind)}`);
    if (!allowedMaturity.has(metadata.maturity)) {
      errors.push(`${entry.name}: unknown maturity ${JSON.stringify(metadata.maturity)}`);
    }

    if (byId.has(metadata.id)) errors.push(`${entry.name}: duplicate id ${metadata.id}`);
    else byId.set(metadata.id, entry);

    if (metadata.facets == null || typeof metadata.facets !== "object" || Array.isArray(metadata.facets)) {
      errors.push(`${entry.name}: facets must be an object`);
    } else {
      for (const [family, values] of Object.entries(metadata.facets)) {
        if (!allowedFacetFamilies.has(family)) errors.push(`${entry.name}: unknown facet family ${family}`);
        if (!Array.isArray(values)) {
          errors.push(`${entry.name}: facet ${family} must be an array`);
          continue;
        }
        for (const value of values) {
          if (typeof value !== "string" || !/^[a-z0-9]+(?:-[a-z0-9]+)*$/.test(value)) {
            errors.push(`${entry.name}: facet ${family} contains invalid value ${JSON.stringify(value)}`);
          }
        }
      }
    }

    if (!Array.isArray(metadata.aliases)) errors.push(`${entry.name}: aliases must be an array`);
    if (!Array.isArray(metadata.relations)) errors.push(`${entry.name}: relations must be an array`);
    if (!Array.isArray(metadata.cases)) errors.push(`${entry.name}: cases must be an array`);
  }

  for (const entry of entries) {
    if (!entry.metadata || !Array.isArray(entry.metadata.relations)) continue;
    for (const relation of entry.metadata.relations) {
      if (relation == null || typeof relation !== "object") {
        errors.push(`${entry.name}: relation must be an object`);
        continue;
      }
      if (typeof relation.type !== "string" || typeof relation.target !== "string") {
        errors.push(`${entry.name}: relation requires string type and target`);
        continue;
      }
      if (/^[a-z0-9]+(?:-[a-z0-9]+)*$/.test(relation.target) && !byId.has(relation.target)) {
        errors.push(`${entry.name}: local relation target does not exist: ${relation.target}`);
      }
    }
  }

  if (errors.length > 0) {
    for (const error of errors) console.error(`ERROR ${error}`);
    return false;
  }

  console.log(`Validated ${entries.length} compendium entries.`);
  return true;
}

function normalizedEntries(entries) {
  return entries.filter((entry) => entry.metadata).map((entry) => ({ ...entry.metadata, text: entry.text }));
}

function list(entries, args) {
  let selected = normalizedEntries(entries);
  const kindIndex = args.indexOf("--kind");
  if (kindIndex >= 0) selected = selected.filter((entry) => entry.kind === args[kindIndex + 1]);

  const facetIndex = args.indexOf("--facet");
  if (facetIndex >= 0) {
    const raw = args[facetIndex + 1] ?? "";
    const split = raw.indexOf("=");
    if (split < 1) throw new Error("--facet expects family=value");
    const family = raw.slice(0, split);
    const value = raw.slice(split + 1);
    selected = selected.filter((entry) => entry.facets?.[family]?.includes(value));
  }

  for (const entry of selected) console.log(`${entry.id}\t${entry.kind}\t${entry.maturity}`);
}

function show(entries, id) {
  const entry = normalizedEntries(entries).find((candidate) => candidate.id === id);
  if (!entry) throw new Error(`unknown entry: ${id}`);
  const { text: _text, ...metadata } = entry;
  console.log(JSON.stringify(metadata, null, 2));
}

function related(entries, id) {
  const all = normalizedEntries(entries);
  const entry = all.find((candidate) => candidate.id === id);
  if (!entry) throw new Error(`unknown entry: ${id}`);

  for (const relation of entry.relations ?? []) {
    console.log(`${id}\t${relation.type}\t${relation.target}`);
  }
  for (const candidate of all) {
    for (const relation of candidate.relations ?? []) {
      if (relation.target === id) console.log(`${candidate.id}\t${relation.type}\t${id}`);
    }
  }
}

function search(entries, queryParts) {
  const query = queryParts.join(" ").trim().toLowerCase();
  if (!query) throw new Error("search requires a query");
  const terms = query.split(/\s+/).filter(Boolean);

  const scored = normalizedEntries(entries)
    .map((entry) => {
      const haystack = [
        entry.id,
        entry.kind,
        entry.maturity,
        ...(entry.aliases ?? []),
        ...Object.values(entry.facets ?? {}).flat(),
        entry.text,
      ]
        .join("\n")
        .toLowerCase();
      const score = terms.reduce((total, term) => total + (haystack.includes(term) ? 1 : 0), 0);
      return { entry, score };
    })
    .filter(({ score }) => score > 0)
    .sort((a, b) => b.score - a.score || a.entry.id.localeCompare(b.entry.id));

  for (const { entry, score } of scored) console.log(`${score}\t${entry.id}\t${entry.kind}`);
}

function main() {
  const entries = loadEntries();
  const [command = "validate", ...args] = process.argv.slice(2);

  if (command === "validate") {
    if (!validate(entries)) process.exitCode = 1;
    return;
  }

  if (!validate(entries)) return;

  if (command === "list") list(entries, args);
  else if (command === "show") show(entries, args[0]);
  else if (command === "related") related(entries, args[0]);
  else if (command === "search") search(entries, args);
  else throw new Error(`unknown command: ${command}`);
}

try {
  main();
} catch (error) {
  die(error instanceof Error ? error.message : String(error));
}
