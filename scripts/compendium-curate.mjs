#!/usr/bin/env node

import fs from "node:fs";
import path from "node:path";
import process from "node:process";

const root = process.cwd();
const entriesDir = path.join(root, "compendium", "entries");

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
      if (!match) throw new Error(`${name}: missing metadata JSON block`);

      let metadata;
      try {
        metadata = JSON.parse(match[1]);
      } catch (error) {
        throw new Error(`${name}: invalid metadata JSON: ${error.message}`);
      }

      return {
        ...metadata,
        text,
        source: path.relative(root, file),
      };
    });
}

function allEdges(entries) {
  const edges = [];
  for (const entry of entries) {
    for (const relation of entry.relations ?? []) {
      edges.push({ source: entry.id, type: relation.type, target: relation.target });
    }
  }
  return edges;
}

function hasBoundarySection(text) {
  return /^##\s+(Limits(?: and counterexamples)?|Counterexamples?|Boundaries|Where it does not apply)\s*$/im.test(text);
}

function buildQueues(entries) {
  const edges = allEdges(entries);
  const degree = new Map(entries.map((entry) => [entry.id, 0]));

  for (const edge of edges) {
    degree.set(edge.source, (degree.get(edge.source) ?? 0) + 1);
    degree.set(edge.target, (degree.get(edge.target) ?? 0) + 1);
  }

  const ids = (predicate) =>
    entries
      .filter(predicate)
      .map((entry) => entry.id)
      .sort();

  return [
    {
      id: "missing-case-evidence",
      description: "Entries with no concrete case references; inspect whether they need evidence links or should remain purely conceptual.",
      entries: ids((entry) => (entry.cases ?? []).length === 0),
    },
    {
      id: "graph-orphans",
      description: "Entries with no incoming or outgoing typed relationships; inspect whether they are intentionally standalone or under-connected.",
      entries: ids((entry) => (degree.get(entry.id) ?? 0) === 0),
    },
    {
      id: "thin-candidates",
      description: "Candidate entries with one or zero concrete cases; good targets for a sibling case, counterexample, split, or retirement check.",
      entries: ids((entry) => entry.maturity === "candidate" && (entry.cases ?? []).length <= 1),
    },
    {
      id: "supported-evidence-review",
      description: "Supported entries with one or zero concrete cases; support may still be valid, but the evidence basis is worth an explicit review.",
      entries: ids((entry) => entry.maturity === "supported" && (entry.cases ?? []).length <= 1),
    },
    {
      id: "mature-boundary-review",
      description: "Mature entries without an obvious Limits/Counterexamples/Boundaries section; inspect whether the abstraction records what would make it false.",
      entries: ids((entry) => entry.maturity === "mature" && !hasBoundarySection(entry.text)),
    },
    {
      id: "low-connectivity",
      description: "Entries with at most one graph edge; review whether a useful invariant, repair, technique, specialization, or counterexample link is missing.",
      entries: ids((entry) => (degree.get(entry.id) ?? 0) <= 1),
    },
    {
      id: "weakly-linked-executable-graduations",
      description: "Executable-graduation records with fewer than two graph edges; inspect whether the executable result links back to the lesson it enforces.",
      entries: ids(
        (entry) => entry.kind === "executable-graduation" && (degree.get(entry.id) ?? 0) < 2,
      ),
    },
  ];
}

function report(entries) {
  const queues = buildQueues(entries);
  return {
    schema: 1,
    generated_from: "compendium/entries",
    entries: entries.length,
    queues,
  };
}

function printHuman(result) {
  console.log(`Compendium curation hints for ${result.entries} entries.`);
  console.log("These are review prompts, not validation failures.\n");

  for (const queue of result.queues) {
    console.log(`${queue.id} (${queue.entries.length})`);
    console.log(`  ${queue.description}`);
    if (queue.entries.length === 0) {
      console.log("  [none]");
    } else {
      for (const id of queue.entries.slice(0, 20)) console.log(`  - ${id}`);
      if (queue.entries.length > 20) console.log(`  ... ${queue.entries.length - 20} more`);
    }
    console.log("");
  }
}

function main() {
  const entries = loadEntries();
  const result = report(entries);

  if (process.argv.includes("--json")) {
    console.log(JSON.stringify(result, null, 2));
    return;
  }

  printHuman(result);
}

try {
  main();
} catch (error) {
  die(error instanceof Error ? error.message : String(error));
}
