import fs from 'node:fs/promises';

const CODE_EXTENSIONS = /\.(ts|tsx|js|jsx|mts|mjs|cts|cjs)$/;
const TEST_FILE_PATTERNS =
  /\.(test|spec)\.(ts|tsx|js|jsx|mts|mjs|cts|cjs)$|\.test-d\.ts$/;

const changedChangesets = ['.changeset/quiet-stream-errors-release.md'];
const changedPackageFiles = [
  'packages/ai/src/util/async-iterable-stream.ts',
  'packages/ai/src/util/async-iterable-stream-read-error.test.ts',
];

function isCodeFile(path) {
  if (!path.startsWith('packages/')) return false;
  if (TEST_FILE_PATTERNS.test(path)) return false;
  if (path.endsWith('.md')) return false;
  return CODE_EXTENSIONS.test(path);
}

const changesets = [];
for (const path of changedChangesets) {
  if (!/^\.changeset\/[a-z0-9-]+\.md/.test(path)) {
    throw new Error('invalid changeset path');
  }

  const content = await fs.readFile(new URL(path, import.meta.url), 'utf8');
  const match = content.match(/---\n([\s\S]+?)\n---/);
  if (!match) throw new Error('missing changeset frontmatter');

  const versionBumps = {};
  for (const line of match[1].split('\n')) {
    const [rawName, bump] = line.split(':').map(value => value.trim());
    const name = rawName.replace(/^['"]|['"]$/g, '');
    if (!name || !bump) throw new Error('invalid changeset frontmatter');
    if (bump !== 'patch') throw new Error('non-patch version bump');
    versionBumps[name] = bump;
  }
  changesets.push({ path, versionBumps });
}

const codeFiles = changedPackageFiles.filter(isCodeFile);
const packageDirs = [
  ...new Set(codeFiles.map(path => path.split('/').slice(0, 2).join('/'))),
];
const changedPackageNames = [];
for (const dir of packageDirs) {
  const pkg = JSON.parse(
    await fs.readFile(new URL(`${dir}/package.json`, import.meta.url), 'utf8'),
  );
  if (pkg.name && !pkg.private) changedPackageNames.push(pkg.name);
}

const coveredPackages = new Set(
  changesets.flatMap(changeset => Object.keys(changeset.versionBumps)),
);
const missingPackages = changedPackageNames.filter(
  name => !coveredPackages.has(name),
);
if (missingPackages.length > 0) {
  throw new Error(`missing packages: ${missingPackages.join(', ')}`);
}

console.log(
  JSON.stringify(
    {
      status: 'passed',
      codeFiles,
      changedPackageNames,
      coveredPackages: [...coveredPackages],
    },
    null,
    2,
  ),
);
