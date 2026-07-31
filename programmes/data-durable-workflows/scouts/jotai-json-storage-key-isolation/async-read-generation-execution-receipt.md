# Jotai asynchronous read-generation repair execution receipt

Issue: #282

Parent finding: #235

State: target-executed research repair; direct owned-source materialization pending

Upstream contact authorized: false

## Exact identity

- Jotai target source: `56a9cc51de8a5dd762b95a145820f12589cc47c9`
- selected key-isolation Fieldwork base: `d9dd61c4a0d1f9073c300519990e6ba9ec2855d9`
- asynchronous-read characterization head: `2fb60bd0497d5557afb54d11c3d6d1a31020b312`
- executed repair head: `e99c7d2e9e3b16c04b1738397ad6109758ad481e`
- repair branch: `repair/282-jotai-async-read-generation-counter`
- complete-diff review: `4827783876`, `ACCEPT` for direct owned-source materialization

## Exact execution

- Fieldwork integrity run `30623229093`: success
- generation-repair run `30623229098`: success on Node 22, Node 24, and Node 26
- selected key-scoped cache run `30623229114`: success
- inspected Node 24 job `91132389642`: 43 focused and adjacent tests passed, followed by ESLint, Prettier, and TypeScript checks

The executed source fence contained the selected key-scoped cache patch, the generation-counter patch, three focused regression files, and the existing `atomWithStorage` suite.

## Accepted bounded mechanism

- each read captures a new monotonically increasing generation for its key;
- a valid or malformed read completion changes shared cache state only while its generation remains current;
- completed removal advances that key's generation before deleting cached identity;
- every caller still receives its own backend result even when that result is no longer authoritative for shared cache publication;
- unrelated-key cache identity remains stable;
- generation retention follows the selected adapter-lifetime per-key retention policy.

## Reversing controls retained

The focused controls prove that the repair prevents:

- an older same-key read from replacing a newer completion;
- a pre-removal read from repopulating cache authority after removal settles;
- an older valid read from restoring authority after a newer missing or malformed result;
- a stale malformed completion from deleting a newer valid identity;
- cross-key generation interference.

## Evidence boundary

This is target-executed evidence for asynchronous `getItem` completion versus other reads and completed `removeItem` settlement at the exact Jotai source revision above.

It does not establish ordering between reads and `setItem`; complete target-repository compatibility beyond the named suites; production behavior; merge readiness; or public-upstream acceptance. Read/write operation authority remains a separate question.

## Carrier retirement

The one-off Fieldwork execution workflow may be removed after this receipt is committed because the exact source, run, review, and claim boundary are retained here. Removing that workflow does not mean the target tests reran on the later cleanup head.

## Next transition

Materialize the exact accepted source change and native controls on one directly owned Jotai source branch, run the repository's declared complete gates, transfer those receipts, and obtain a fresh complete-diff review. No public upstream interaction is authorized.
