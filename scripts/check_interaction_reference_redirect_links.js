const legacy = require('./check_interaction_references.js');

const POLICY_COMMENT = '<!-- fieldwork-reference-policy-result -->';
const VIOLATION_LABEL = 'policy:reference-violation';
const MAX_COMMENT_DIAGNOSTICS = 100;

function escapeRegExp(value) {
  return value.replace(/[.*+?^${}()|[\]\\]/g, '\\$&');
}

function maskMatchingShorthand(label, owner, repository, item) {
  const target = new RegExp(
    `(^|[^A-Za-z0-9_.-])(${escapeRegExp(owner)}\\/${escapeRegExp(repository)}#${escapeRegExp(item)})\\b`,
    'gi',
  );

  return label.replace(target, (match, prefix, shorthand) => {
    return `${prefix}${' '.repeat(shorthand.length)}`;
  });
}

function maskCompliantRedirectLinkLabels(text) {
  if (!text) return text;

  const redirectLink =
    /\[([^\]\r\n]+)\](\(\s*<?https?:\/\/redirect\.github\.com\/([A-Za-z0-9_.-]+)\/([A-Za-z0-9_.-]+)\/(issues|pull|discussions)\/([0-9]+)(?:[/?#][^>\s)]*)?>?(?:\s+(?:"[^"\r\n]*"|'[^'\r\n]*'|\([^\)\r\n]*\)))?\s*\))/gi;

  return text.replace(
    redirectLink,
    (match, label, destination, owner, repository, kind, item) => {
      const maskedLabel = maskMatchingShorthand(label, owner, repository, item);
      return `[${maskedLabel}]${destination}`;
    },
  );
}

function scan(text, currentRepository, ownedOwners) {
  return legacy.scan(
    maskCompliantRedirectLinkLabels(text),
    currentRepository,
    ownedOwners,
  );
}

function scanEntries(entries, currentRepository, ownedOwners) {
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

async function run({ github, context, core }) {
  const commentBody = context.payload.comment?.body || '';
  if (commentBody.includes(POLICY_COMMENT)) return;

  const issueNumber = issueNumberFromContext(context);
  if (!issueNumber) return;

  const currentRepository = `${context.repo.owner}/${context.repo.repo}`.toLowerCase();
  const { entries, comments } = await legacy.collectThreadEntries({
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
  const body = legacy.policyCommentBody(failures);

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
    core.setFailed(
      `Found ${failures.length} external reference policy violation(s) in the complete interaction thread.`,
    );
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
    const { entries } = await legacy.collectThreadEntries({
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

  const violationCount = findings.reduce(
    (total, finding) => total + finding.failures.length,
    0,
  );
  core.setFailed(
    `Found ${violationCount} external reference policy violation(s) across ${findings.length} interaction thread(s).`,
  );
  return findings;
}

module.exports = run;
module.exports.auditRepository = auditRepository;
module.exports.maskCompliantRedirectLinkLabels = maskCompliantRedirectLinkLabels;
module.exports.scan = scan;
module.exports.scanEntries = scanEntries;
