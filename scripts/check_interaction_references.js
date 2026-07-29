const POLICY_COMMENT = '<!-- fieldwork-reference-policy-result -->';
const INTENTIONAL_MARKER = 'fieldwork: intentional-upstream-reference';
const VIOLATION_LABEL = 'policy:reference-violation';
const DEFAULT_OWNED_OWNERS = new Set(['teamleaderleo']);

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
  const direct = /https?:\/\/github\.com\/([A-Za-z0-9_.-]+)\/([A-Za-z0-9_.-]+)\/(issues|pull|discussions|commit)\/([A-Za-z0-9_.-]+)/g;
  const shorthand = /(^|[^A-Za-z0-9_.-])([A-Za-z0-9_.-]+)\/([A-Za-z0-9_.-]+)#([0-9]+)\b/g;

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
      failures.push(`Line ${index + 1}: direct third-party GitHub reference: ${match[0]}`);
    }

    for (const match of line.matchAll(shorthand)) {
      const owner = match[2];
      const repository = `${owner}/${match[3]}`.toLowerCase();
      if (isControlledRepository(repository, owner, currentRepository, ownedOwners)) continue;
      failures.push(
        `Line ${index + 1}: third-party shorthand reference: ${match[2]}/${match[3]}#${match[4]}`,
      );
    }
  }

  return [...new Set(failures)];
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
  const payload = context.payload;
  const actorType = payload.sender?.type;
  const commentBody = payload.comment?.body || '';

  if (actorType === 'Bot' || commentBody.includes(POLICY_COMMENT)) return;

  let subject = '';
  if (context.eventName === 'issues') {
    subject = `${payload.issue?.title || ''}\n${payload.issue?.body || ''}`;
  } else if (context.eventName === 'pull_request_target') {
    subject = `${payload.pull_request?.title || ''}\n${payload.pull_request?.body || ''}`;
  } else if (context.eventName === 'issue_comment') {
    subject = commentBody;
  } else if (context.eventName === 'pull_request_review') {
    subject = payload.review?.body || '';
  } else if (context.eventName === 'pull_request_review_comment') {
    subject = commentBody;
  } else {
    return;
  }

  const currentRepository = `${context.repo.owner}/${context.repo.repo}`.toLowerCase();
  const failures = scan(subject, currentRepository);
  const issueNumber = payload.issue?.number || payload.pull_request?.number || context.issue.number;

  await setViolationLabel({
    github,
    context,
    issueNumber,
    violated: failures.length > 0,
  });

  const comments = await github.paginate(github.rest.issues.listComments, {
    owner: context.repo.owner,
    repo: context.repo.repo,
    issue_number: issueNumber,
    per_page: 100,
  });
  const existing = comments.find(
    (comment) => comment.user?.type === 'Bot' && comment.body?.includes(POLICY_COMMENT),
  );

  let body;
  if (failures.length === 0) {
    if (!existing) return;
    body = `${POLICY_COMMENT}\nExternal reference policy check now passes for the latest edited interaction.`;
  } else {
    const details = failures.map((failure) => `- ${failure}`).join('\n');
    body = `${POLICY_COMMENT}\nThird-party GitHub references are quiet by default. Direct links and shorthand within \`teamleaderleo/*\` are allowed. Replace direct third-party issue, pull-request, discussion, and commit references with \`redirect.github.com\`. Remove third-party shorthand. Use the intentional-upstream marker only when that exact interaction was explicitly authorized.\n\n${details}`;
    core.setFailed(`Found ${failures.length} external reference policy violation(s).`);
  }

  if (existing) {
    await github.rest.issues.updateComment({
      owner: context.repo.owner,
      repo: context.repo.repo,
      comment_id: existing.id,
      body,
    });
  } else {
    await github.rest.issues.createComment({
      owner: context.repo.owner,
      repo: context.repo.repo,
      issue_number: issueNumber,
      body,
    });
  }
}

module.exports = run;
module.exports.scan = scan;
module.exports.configuredOwnedOwners = configuredOwnedOwners;
