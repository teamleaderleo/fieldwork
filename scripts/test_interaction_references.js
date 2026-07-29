const assert = require('node:assert/strict');
const { scan } = require('./check_interaction_references.js');

const current = 'teamleaderleo/fieldwork';

assert.equal(scan('', current).length, 0);
assert.equal(scan('https://redirect.github.com/example/project/issues/12', current).length, 0);
assert.equal(scan('https://github.com/example/project', current).length, 0);
assert.equal(scan('https://github.com/teamleaderleo/fieldwork/issues/1', current).length, 0);
assert.equal(scan('https://github.com/example/project/issues/12', current).length, 1);
assert.equal(scan('example/project#12', current).length, 1);

const marked = [
  '<!-- fieldwork: intentional-upstream-reference -->',
  'https://github.com/example/project/issues/12',
].join('\n');
assert.equal(scan(marked, current).length, 0);

const distantMarker = [
  '<!-- fieldwork: intentional-upstream-reference -->',
  'authorized line',
  'https://github.com/example/project/issues/12',
].join('\n');
assert.equal(scan(distantMarker, current).length, 1);

console.log('Interaction reference tests passed.');
