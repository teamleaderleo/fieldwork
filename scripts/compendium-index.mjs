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
const allowedRelationTypes = new Set([
  "violates",
  "illustrates",
  "related-to",
  "detected-by",
  "repaired-by",
  "protected-by",
  "clarifies",
  "counterexample-to",
  "specializes",
  "generalizes",
  "graduated-to",
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
    else {
      for (const alias of metadata.aliases) {
        if (typeof alias !== "string" || alias.trim() === "") errors.push(`${entry.name}: aliases must contain non-empty strings`);
      }
    }

    if (!Array.isArray(metadata.relations)) errors.push(`${entry.name}: relations must be an array`);
    if (!Array.isArray(metadata.cases)) errors.push(`${entry.name}: cases must be an array`);
    else {
      for (const caseRef of metadata.cases) {
        if (typeof caseRef !== "string" || caseRef.trim() === "") errors.push(`${entry.name}: cases must contain non-empty strings`);
      }
      if (new Set(metadata.cases).size !== metadata.cases.length) errors.push(`${entry.name}: cases must not contain duplicates`);
    }
  }

  for (const entry of entries) {
    if (!entry.metadata || !Array.isArray(entry.metadata.relations)) continue;
    for (const relation of entry.metadata.relations) {
      if (relation == null || typeof relation !== "object" || Array.isArray(relation)) {
        errors.push(`${entry.name}: relation must be an object`);
        continue;
      }
      if (typeof relation.type !== "string" || typeof relation.target !== "string") {
        errors.push(`${entry.name}: relation requires string type and target`);
        continue;
      }
      if (!allowedRelationTypes.has(relation.type)) {
        errors.push(`${entry.name}: unknown relation type ${JSON.stringify(relation.type)}`);
      }
      if (!/^[a-z0-9]+(?:-[a-z0-9]+)*$/.test(relation.target)) {
        errors.push(`${entry.name}: relation target must be a local kebab-case entry id: ${JSON.stringify(relation.target)}`);
        continue;
      }
      if (!byId.has(relation.target)) {
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

function extractSummary(text) {
  const match = text.match(/## In simple words\s*\n+([\s\S]*?)(?=\n## |\s*$)/);
  if (!match) return "";
  const summary = match[1].trim().replace(/\n{3,}/g, "\n\n");
  return summary.length <= 1600 ? summary : `${summary.slice(0, 1597)}...`;
}

function normalizedEntries(entries) {
  return entries
    .filter((entry) => entry.metadata)
    .map((entry) => ({
      ...entry.metadata,
      source: path.relative(root, entry.file),
      summary: extractSummary(entry.text),
      text: entry.text,
    }));
}

function metadataView(entry) {
  const { text: _text, ...metadata } = entry;
  return metadata;
}

function buildById(entries) {
  return new Map(normalizedEntries(entries).map((entry) => [entry.id, entry]));
}

function allEdges(entries) {
  const edges = [];
  for (const entry of normalizedEntries(entries)) {
    for (const relation of entry.relations ?? []) {
      edges.push({ source: entry.id, type: relation.type, target: relation.target });
    }
  }
  return edges;
}

function list(entries, args) {
  let selected = normalizedEntries(entries);
  const kindIndex = args.indexOf("--kind");
  if (kindIndex >= 0) selected = selected.filter((entry) => entry.kind === args[kindIndex + 1]);

  const facetIndices = args.flatMap((arg, index) => (arg === "--facet" ? [index] : []));
  for (const facetIndex of facetIndices) {
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
  const entry = buildById(entries).get(id);
  if (!entry) throw new Error(`unknown entry: ${id}`);
  console.log(JSON.stringify(metadataView(entry), null, 2));
}

function related(entries, id) {
  const byId = buildById(entries);
  if (!byId.has(id)) throw new Error(`unknown entry: ${id}`);

  for (const edge of allEdges(entries)) {
    if (edge.source === id || edge.target === id) {
      console.log(`${edge.source}\t${edge.type}\t${edge.target}`);
    }
  }
}

function scoreSearch(entries, queryParts) {
  const query = queryParts.join(" ").trim().toLowerCase();
  if (!query) throw new Error("search requires a query");
  const terms = query.split(/\s+/).filter(Boolean);

  return normalizedEntries(entries)
    .map((entry) => {
      const strongHaystack = [entry.id, ...(entry.aliases ?? []), ...Object.values(entry.facets ?? {}).flat()]
        .join("\n")
        .toLowerCase();
      const bodyHaystack = entry.text.toLowerCase();
      const score = terms.reduce((total, term) => {
        if (strongHaystack.includes(term)) return total + 3;
        if (bodyHaystack.includes(term)) return total + 1;
        return total;
      }, 0);
      return { entry, score };
    })
    .filter(({ score }) => score > 0)
    .sort((a, b) => b.score - a.score || a.entry.id.localeCompare(b.entry.id));
}

function search(entries, queryParts) {
  for (const { entry, score } of scoreSearch(entries, queryParts)) {
    console.log(`${score}\t${entry.id}\t${entry.kind}`);
  }
}

function packet(entries, id, args) {
  const byId = buildById(entries);
  if (!byId.has(id)) throw new Error(`unknown entry: ${id}`);

  const depthIndex = args.indexOf("--depth");
  const depth = depthIndex >= 0 ? Number.parseInt(args[depthIndex + 1], 10) : 1;
  if (!Number.isInteger(depth) || depth < 0 || depth > 2) throw new Error("--depth must be 0, 1, or 2");

  const edges = allEdges(entries);
  const selected = new Set([id]);
  let frontier = new Set([id]);

  for (let level = 0; level < depth; level += 1) {
    const next = new Set();
    for (const edge of edges) {
      if (frontier.has(edge.source) && !selected.has(edge.target)) next.add(edge.target);
      if (frontier.has(edge.target) && !selected.has(edge.source)) next.add(edge.source);
    }
    for (const candidate of next) selected.add(candidate);
    frontier = next;
  }

  if (selected.size > 50) throw new Error(`packet expanded to ${selected.size} entries; reduce --depth`);

  const packetEntries = [...selected]
    .sort()
    .map((entryId) => metadataView(byId.get(entryId)));
  const packetEdges = edges.filter((edge) => selected.has(edge.source) && selected.has(edge.target));
  const cases = [...new Set(packetEntries.flatMap((entry) => entry.cases ?? []))].sort();

  console.log(
    JSON.stringify(
      {
        schema: 1,
        root: id,
        depth,
        entries: packetEntries,
        relations: packetEdges,
        cases,
      },
      null,
      2,
    ),
  );
}

function exportIndex(entries) {
  console.log(
    JSON.stringify(
      {
        schema: 1,
        generated_from: "compendium/entries",
        entries: normalizedEntries(entries).map(metadataView),
        relations: allEdges(entries),
      },
      null,
      2,
    ),
  );
}

function stats(entries) {
  const all = normalizedEntries(entries);
  const countBy = (values) =>
    Object.fromEntries(
      [...new Set(values)]
        .sort()
        .map((value) => [value, values.filter((candidate) => candidate === value).length]),
    );

  const facets = {};
  for (const family of allowedFacetFamilies) {
    facets[family] = countBy(all.flatMap((entry) => entry.facets?.[family] ?? []));
  }

  console.log(
    JSON.stringify(
      {
        entries: all.length,
        relations: allEdges(entries).length,
        cases: new Set(all.flatMap((entry) => entry.cases ?? [])).size,
        kinds: countBy(all.map((entry) => entry.kind)),
        maturity: countBy(all.map((entry) => entry.maturity)),
        facets,
      },
      null,
      2,
    ),
  );
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
  else if (command === "packet") packet(entries, args[0], args.slice(1));
  else if (command === "export") exportIndex(entries);
  else if (command === "stats") stats(entries);
  else throw new Error(`unknown command: ${command}`);
}

try {
  main();
} catch (error) {
  die(error instanceof Error ? error.message : String(error));
}
