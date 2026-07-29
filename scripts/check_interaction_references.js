const fs = require('node:fs');

const POLICY_COMMENT = '<!-- fieldwork-reference-policy-result -->';
const INTENTIONAL_MARKER = 'fieldwork: intentional-upstream-reference';
const VIOLATION_LABEL = 'policy:reference-violation';
const DEFAULT_REPOSITORY = 'teamleaderleo/fieldwork';
const DEFAULT_OWNED_OWNERS = new Set(['teamleaderleo']);
const MAX_COMMENT_DIAGNOSTICS = 100;

function configuredOwnedOwners() {
  const configured = process.env.FIELDWORK_OWNED_GITHUB_OWNERS;
  if (!configured) return new Set(DEFAULT_OWNED_OWNERS);

  return new Set(
    configured
      .split(',')
      .map((owner) => owner.trim().toLowerCase())
      .filter(Boolean),
  );
}

function isControlledRepository(repository, owner, currentRepository, ownedOwners) {
  return repository === currentRepository || ownedOwners.has(owner.toLowerCase());
}

function scan(text, currentRepository, ownedOwners = configuredOwnedOwners()) {
  if (!text) return [];

  const failures = [];
  const lines = text.split(/\r?\n/);
  const direct =
    /https?:\/\/github\.com\/([A-Za-z0-9_.-]+)\/([A-Za-z0-9_.-]+)\/(issues|pull|discussions|commit)\/([A-Za-z0-9_.-]+)/g;
  const shorthand =
    /(^|[^A-Za-z0-9_.-])([A-Za-z0-9_.-]+)\/([A-Za-z0-9_.-]+)#([0-9]+)\b/g;
  const commitShorthand =
    /(^|[^A-Za-z0-9_.-])([A-Za-z0-9_.-]+)\/([A-Za-z0-9_.-]+)@([0-9a-fA-F]{7,40})\b/g;

  for (let index = 0; index < lines.length; index += 1) {
    const line = lines[index];
    const intentional =
      line.includes(INTENTIONAL_MARKER) ||
      (index > 0 && lines[index - 1].includes(INTENTIONAL_MARKER));

    if (intentional) continue;

    for (const match of line.matchAll(direct)) {
      const owner = match[1];
      const repository = `${owner}/${match[2]}`.toLowerCase();
      if (isControlledRepository(repository, owner, currentRepository, ownedOwners)) continue;
      failures.push(
        `Line ${index + 1}: direct third-party GitHub reference detected (${owner} / ${match[2]}, ${match[3]} ${match[4]}).`,
      );
    }

    for (const match of line.matchAll(shorthand)) {
      const owner = match[2];
      const repository = `${owner}/${match[3]}`.toLowerCase();
      if (isControlledRepository(repository, owner, currentRepository, ownedOwners)) continue;
      failures.push(
        `Line ${index + 1}: third-party shorthand reference detected (${match[2]} / ${match[3]}, item ${match[4]}).`,
      );
    }

    for (const match of line.matchAll(commitShorthand)) {
      const owner = match[2];
      const repository = `${owner}/${match[3]}`.toLowerCase();
      if (isControlledRepository(repository, owner, currentRepository, ownedOwners)) continue;
      failures.push(
        `Line ${index + 1}: third-party commit shorthand detected (${match[2]} / ${match[3]}, commit ${match[4].slice(0, 12)}).`,
      );
    }
  }

  return [...new Set(failures)];
}

function scanEntries(entries, currentRepository, ownedOwners = configuredOwnedOwners()) {
  const failures = [];
  for (const entry of entries) {
    for (const failure of scan(entry.text, currentRepository, ownedOwners)) {
      failures.push(`${entry.source}: ${failure}`);
    }
  }
  return failures;
}

function issueNumberFromContext(context) {
  return (
    context.payload.issue?.number ||
    context.payload.pull_request?.number ||
    context.issue?.number ||
    null
  );
}

function shouldSkipComment(comment) {
  return Boolean(comment.body?.includes(POLICY_COMMENT));
}

async function collectThreadEntries({ github, context, issueNumber }) {
  const { data: issue } = await github.rest.issues.get({
    owner: context.repo.owner,
    repo: context.repo.repo,
    issue_number: issueNumber,
  });

  const entries = [
    {
      source: issue.pull_request ? `pull request #${issueNumber} body` : `issue #${issueNumber} body`,
      text: `${issue.title || ''}\n${issue.body || ''}`,
    },
  ];

  const comments = await github.paginate(github.rest.issues.listComments, {
    owner: context.repo.owner,
    repo: context.repo.repo,
    issue_number: issueNumber,
    per_page: 100,
  });

  for (const comment of comments) {
    if (shouldSkipComment(comment)) continue;
    entries.push({
      source: `comment ${comment.id}`,
      text: comment.body || '',
    });
  }

  if (issue.pull_request) {
    const reviews = await github.paginate(github.rest.pulls.listReviews, {
      owner: context.repo.owner,
      repo: context.repo.repo,
      pull_number: issueNumber,
      per_page: 100,
    });

    for (const review of reviews) {
      entries.push({
        source: `review ${review.id}`,
        text: review.body || '',
      });
    }

    const reviewComments = await github.paginate(github.rest.pulls.listReviewComments, {
      owner: context.repo.owner,
      repo: context.repo.repo,
      pull_number: issueNumber,
      per_page: 100,
    });

    for (const comment of reviewComments) {
      entries.push({
        source: `review comment ${comment.id}`,
        text: comment.body || '',
      });
    }
  }

  return { issue, entries, comments };
}

async function setViolationLabel({ github, context, issueNumber, violated }) {
  if (violated) {
    await github.rest.issues.addLabels({
      owner: context.repo.owner,
      repo: context.repo.repo,
      issue_number: issueNumber,
      labels: [VIOLATION_LABEL],
    });
    return;
  }

  try {
    await github.rest.issues.removeLabel({
      owner: context.repo.owner,
      repo: context.repo.repo,
      issue_number: issueNumber,
      name: VIOLATION_LABEL,
    });
  } catch (error) {
    if (error.status !== 404) throw error;
  }
}

function policyCommentBody(failures) {
  if (failures.length === 0) {
    return `${POLICY_COMMENT}\nExternal reference policy check now passes for the complete interaction thread.`;
  }

  const shown = failures.slice(0, MAX_COMMENT_DIAGNOSTICS);
  const details = shown.map((failure) => `- ${failure}`).join('\n');
  const omitted =
    failures.length > shown.length
      ? `\n- ${failures.length - shown.length} additional violation(s) omitted from this comment.`
      : '';

  return `${POLICY_COMMENT}
Third-party GitHub references are quiet by default. Direct links and shorthand within \`teamleaderleo/*\` are allowed. Replace direct third-party issue, pull-request, discussion, and commit references with \`redirect.github.com\`. Remove third-party item and commit shorthand. Use the intentional-upstream marker only when that exact interaction was explicitly authorized.

${details}${omitted}`;
}

async function run({ github, context, core }) {
  const commentBody = context.payload.comment?.body || '';
  if (commentBody.includes(POLICY_COMMENT)) return;

  const issueNumber = issueNumberFromContext(context);
  if (!issueNumber) return;

  const currentRepository = `${context.repo.owner}/${context.repo.repo}`.toLowerCase();
  const { entries, comments } = await collectThreadEntries({
    github,
    context,
    issueNumber,
  });
  const failures = scanEntries(entries, currentRepository);

  await setViolationLabel({
    github,
    context,
    issueNumber,
    violated: failures.length > 0,
  });

  const existing = comments.find(
    (comment) => comment.user?.type === 'Bot' && comment.body?.includes(POLICY_COMMENT),
  );
  const body = policyCommentBody(failures);

  if (existing) {
    await github.rest.issues.updateComment({
      owner: context.repo.owner,
      repo: context.repo.repo,
      comment_id: existing.id,
      body,
    });
  } else if (failures.length > 0) {
    await github.rest.issues.createComment({
      owner: context.repo.owner,
      repo: context.repo.repo,
      issue_number: issueNumber,
      body,
    });
  }

  if (failures.length > 0) {
    core.setFailed(`Found ${failures.length} external reference policy violation(s) in the complete interaction thread.`);
  }
}

async function auditRepository({ github, context, core }) {
  const currentRepository = `${context.repo.owner}/${context.repo.repo}`.toLowerCase();
  const issues = await github.paginate(github.rest.issues.listForRepo, {
    owner: context.repo.owner,
    repo: context.repo.repo,
    state: 'all',
    per_page: 100,
  });

  const findings = [];

  for (const issue of issues) {
    const issueNumber = issue.number;
    const { entries } = await collectThreadEntries({
      github,
      context,
      issueNumber,
    });
    const failures = scanEntries(entries, currentRepository);
    if (failures.length === 0) continue;

    findings.push({
      number: issueNumber,
      kind: issue.pull_request ? 'pull request' : 'issue',
      failures,
    });
  }

  if (findings.length === 0) {
    await core.summary
      .addHeading('External reference audit')
      .addParagraph('All active issue and pull-request interaction text passed.')
      .write();
    return [];
  }

  core.summary.addHeading('External reference audit');
  for (const finding of findings) {
    core.summary.addHeading(`${finding.kind} #${finding.number}`, 3);
    core.summary.addList(finding.failures.slice(0, MAX_COMMENT_DIAGNOSTICS));
  }
  await core.summary.write();

  const violationCount = findings.reduce((total, finding) => total + finding.failures.length, 0);
  core.setFailed(
    `Found ${violationCount} external reference policy violation(s) across ${findings.length} interaction thread(s).`,
  );
  return findings;
}

function runCli() {
  const text = fs.readFileSync(0, 'utf8');
  const currentRepository = (
    process.env.FIELDWORK_CURRENT_REPOSITORY || DEFAULT_REPOSITORY
  ).toLowerCase();
  const failures = scan(text, currentRepository);

  if (failures.length === 0) {
    process.stdout.write('Interaction reference preflight passed.\n');
    return;
  }

  process.stderr.write(`${failures.join('\n')}\n`);
  process.exitCode = 1;
}

if (require.main === module) {
  runCli();
}

module.exports = run;
module.exports.auditRepository = auditRepository;
module.exports.collectThreadEntries = collectThreadEntries;
module.exports.configuredOwnedOwners = configuredOwnedOwners;
module.exports.policyCommentBody = policyCommentBody;
module.exports.scan = scan;
module.exports.scanEntries = scanEntries;
