const POLICY_COMMENT = '<!-- fieldwork-reference-policy-result -->';
const INTENTIONAL_MARKER = 'fieldwork: intentional-upstream-reference';

function scan(text, currentRepository) {
  if (!text || text.includes(INTENTIONAL_MARKER)) return [];

  const failures = [];
  const direct = /https?:\/\/github\.com\/([A-Za-z0-9_.-]+)\/([A-Za-z0-9_.-]+)\/(issues|pull|discussions|commit)\/([A-Za-z0-9_.-]+)/g;
  const shorthand = /(^|[^A-Za-z0-9_.-])([A-Za-z0-9_.-]+)\/([A-Za-z0-9_.-]+)#([0-9]+)\b/gm;

  for (const match of text.matchAll(direct)) {
    const repository = `${match[1]}/${match[2]}`.toLowerCase();
    if (repository === currentRepository) continue;
    failures.push(`Direct external GitHub reference: ${match[0]}`);
  }

  for (const match of text.matchAll(shorthand)) {
    const repository = `${match[2]}/${match[3]}`.toLowerCase();
    if (repository === currentRepository) continue;
    failures.push(`External shorthand reference: ${match[2]}/${match[3]}#${match[4]}`);
  }

  return [...new Set(failures)];
}

module.exports = async ({ github, context, core }) => {
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
  } else {
    return;
  }

  const currentRepository = `${context.repo.owner}/${context.repo.repo}`.toLowerCase();
  const failures = scan(subject, currentRepository);
  const issueNumber = context.issue.number;

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
    body = `${POLICY_COMMENT}\nExternal references are quiet by default. Replace direct external issue, pull-request, discussion, and commit references with \`redirect.github.com\`, or add the intentional-upstream marker when contact is explicitly authorized.\n\n${details}`;
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
};
