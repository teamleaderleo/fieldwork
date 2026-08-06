const assert = require('node:assert/strict');
const {
  maskCompliantRedirectLinkLabels,
  scan,
  scanEntries,
} = require('./check_interaction_reference_redirect_links.js');

const current = 'teamleaderleo/fieldwork';
const ownedOwners = new Set(['teamleaderleo']);
const reportedFalsePositive =
  '[openai/codex#37207](https://redirect.github.com/openai/codex/issues/37207)';

assert.equal(scan(reportedFalsePositive, current, ownedOwners).length, 0);
assert.equal(
  scan(
    'Filed as [openai/codex#37207](https://redirect.github.com/openai/codex/issues/37207).',
    current,
    ownedOwners,
  ).length,
  0,
);
assert.equal(
  scan(
    '[OpenAI/Codex#37207](https://redirect.github.com/openai/codex/issues/37207#issuecomment-1)',
    current,
    ownedOwners,
  ).length,
  0,
);
assert.equal(
  scan(
    '[openai/codex#37207](https://redirect.github.com/openai/codex/pull/37207)',
    current,
    ownedOwners,
  ).length,
  0,
);

assert.equal(
  scan(
    '[openai/codex#37207](https://github.com/openai/codex/issues/37207)',
    current,
    ownedOwners,
  ).length,
  2,
);
assert.equal(
  scan(
    '[openai/codex#37207](https://redirect.github.com/openai/codex/issues/37208)',
    current,
    ownedOwners,
  ).length,
  1,
);
assert.equal(
  scan(
    '[openai/codex#37207](https://redirect.github.com/example/project/issues/37207)',
    current,
    ownedOwners,
  ).length,
  1,
);
assert.equal(
  scan(
    '[openai/codex#37207](https://example.com/openai/codex/issues/37207)',
    current,
    ownedOwners,
  ).length,
  1,
);
assert.equal(scan('openai/codex#37207', current, ownedOwners).length, 1);

const multipleReferences =
  '[openai/codex#37207 and example/project#12](https://redirect.github.com/openai/codex/issues/37207)';
const multipleFailures = scan(multipleReferences, current, ownedOwners);
assert.equal(multipleFailures.length, 1);
assert.equal(multipleFailures[0].includes('example / project'), true);

const masked = maskCompliantRedirectLinkLabels(reportedFalsePositive);
assert.equal(masked.includes('openai/codex#37207'), false);
assert.equal(
  masked.includes('https://redirect.github.com/openai/codex/issues/37207'),
  true,
);
assert.equal(masked.length, reportedFalsePositive.length);

const entryFailures = scanEntries(
  [
    { source: 'pull request #613 body', text: reportedFalsePositive },
    { source: 'comment 1', text: 'example/project#12' },
  ],
  current,
  ownedOwners,
);
assert.equal(entryFailures.length, 1);
assert.match(entryFailures[0], /^comment 1:/);

console.log('Interaction redirect-link tests passed.');
