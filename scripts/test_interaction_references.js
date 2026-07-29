const assert = require('node:assert/strict');
const {
  policyCommentBody,
  scan,
  scanEntries,
} = require('./check_interaction_references.js');

const current = 'teamleaderleo/fieldwork';
const ownedOwners = new Set(['teamleaderleo']);

assert.equal(scan('', current, ownedOwners).length, 0);
assert.equal(
  scan('https://redirect.github.com/example/project/issues/12', current, ownedOwners).length,
  0,
);
assert.equal(scan('https://github.com/example/project', current, ownedOwners).length, 0);
assert.equal(
  scan('https://github.com/teamleaderleo/fieldwork/issues/1', current, ownedOwners).length,
  0,
);
assert.equal(
  scan('https://github.com/teamleaderleo/stensibly/issues/490', current, ownedOwners).length,
  0,
);
assert.equal(scan('teamleaderleo/stensibly#490', current, ownedOwners).length, 0);
assert.equal(
  scan(
    'teamleaderleo/stensibly@0123456789abcdef0123456789abcdef01234567',
    current,
    ownedOwners,
  ).length,
  0,
);

const directFailures = scan(
  'https://github.com/example/project/issues/12',
  current,
  ownedOwners,
);
assert.equal(directFailures.length, 1);
assert.equal(scan(directFailures.join('\n'), current, ownedOwners).length, 0);
assert.equal(directFailures[0].includes('github.com'), false);

const shorthandFailures = scan('example/project#12', current, ownedOwners);
assert.equal(shorthandFailures.length, 1);
assert.equal(scan(shorthandFailures.join('\n'), current, ownedOwners).length, 0);
assert.equal(shorthandFailures[0].includes('example/project#12'), false);

const commitFailures = scan(
  'example/project@0123456789abcdef0123456789abcdef01234567',
  current,
  ownedOwners,
);
assert.equal(commitFailures.length, 1);
assert.equal(scan(commitFailures.join('\n'), current, ownedOwners).length, 0);
assert.equal(
  commitFailures[0].includes('example/project@0123456789abcdef0123456789abcdef01234567'),
  false,
);

assert.equal(scan('@biomejs/biome@2.5.6', current, ownedOwners).length, 0);
assert.equal(scan('package/name@2.5.6', current, ownedOwners).length, 0);

const marked = [
  '<!-- fieldwork: intentional-upstream-reference -->',
  'https://github.com/example/project/issues/12',
].join('\n');
assert.equal(scan(marked, current, ownedOwners).length, 0);

const markedCommit = [
  '<!-- fieldwork: intentional-upstream-reference -->',
  'example/project@0123456789abcdef0123456789abcdef01234567',
].join('\n');
assert.equal(scan(markedCommit, current, ownedOwners).length, 0);

const distantMarker = [
  '<!-- fieldwork: intentional-upstream-reference -->',
  'authorized line',
  'https://github.com/example/project/issues/12',
].join('\n');
assert.equal(scan(distantMarker, current, ownedOwners).length, 1);

const additionalOwned = new Set(['teamleaderleo', 'example-owned']);
assert.equal(
  scan(
    'https://github.com/example-owned/project/issues/1',
    current,
    additionalOwned,
  ).length,
  0,
);

const entryFailures = scanEntries(
  [
    { source: 'issue #1 body', text: 'example/project#12' },
    {
      source: 'comment 2',
      text: 'example/project@0123456789abcdef0123456789abcdef01234567',
    },
  ],
  current,
  ownedOwners,
);
assert.equal(entryFailures.length, 2);
assert.match(entryFailures[0], /^issue #1 body:/);
assert.match(entryFailures[1], /^comment 2:/);

const body = policyCommentBody(entryFailures);
assert.equal(scan(body, current, ownedOwners).length, 0);
assert.equal(body.includes('github.com'), true);
assert.equal(body.includes('example/project#12'), false);
assert.equal(
  body.includes('example/project@0123456789abcdef0123456789abcdef01234567'),
  false,
);

console.log('Interaction reference tests passed.');
