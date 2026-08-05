from pathlib import Path

agents_path = Path('AGENTS.md')
start_path = Path('START_HERE.md')

agents = agents_path.read_text(encoding='utf-8')
entry_marker = """## Programme, target, and testbed indexing
"""
activity_section = """## Activity refresh and autonomous continuation

- At the beginning of each work pass, refresh the live state of the relevant owned issues, pull requests, branches, reviews, workflows, queues, and any already-authorized upstream surface before choosing the next action.
- Refresh again after every material transition, including a push, head movement, CI completion, review arrival, superseding patch, duplicate discovery, or evidence transfer.
- Reconcile new activity immediately: inspect completed runs, classify failures, repair owned work, retire duplicates, update stale descriptions, and move evidence to the canonical branch or record.
- Queued CI or awaited review is not a stopping condition. Use that time for complete-diff review, adjacent bounded investigation, harness repair, evidence preservation, or another already-owned lane.
- Do not stop merely to report that work is queued, needs review, or needs repair when the authorized review or repair can be performed. Perform the work and report only a completed result, a genuine blocker, a safety or authority boundary, or a decision that actually requires the user.
- Before every handoff, perform one final activity refresh and make the durable record match the current exact head and live result.
- This loop never expands upstream-contact authority. New public interaction still requires the exact authorization described below.

"""
if activity_section not in agents:
    if agents.count(entry_marker) != 1:
        raise SystemExit('AGENTS.md entry marker changed')
    agents = agents.replace(entry_marker, activity_section + entry_marker, 1)
    agents_path.write_text(agents, encoding='utf-8')

start = start_path.read_text(encoding='utf-8')
start_marker = """## 4. Protect external projects before posting interaction text
"""
start_activity = """### Activity refresh loop

Repeat this loop at the start of a work pass, after every material action, and before handoff:

1. refresh the live issue, pull-request, branch, review, workflow, queue, and relevant already-authorized upstream state for the active lanes;
2. reconcile head changes, completed runs, new reviews, duplicates, supersession, and stale descriptions;
3. perform the next unblocked review or repair immediately;
4. when the primary lane is queued, continue with independent review, bounded adjacent investigation, harness repair, evidence transfer, or another already-owned lane;
5. return to the user only with a completed result, a real blocker, a safety or authority boundary, or a decision that genuinely needs human judgment.

Do not use `queued`, `needs review`, or `needs repair` as a handoff when the authorized work can still be performed. This continuation rule does not authorize public upstream contact.

"""
if start_activity not in start:
    if start.count(start_marker) != 1:
        raise SystemExit('START_HERE.md insertion marker changed')
    start = start.replace(start_marker, start_activity + start_marker, 1)
    start_path.write_text(start, encoding='utf-8')
