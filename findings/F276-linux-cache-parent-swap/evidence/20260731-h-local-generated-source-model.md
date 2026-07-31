# H local generated-source model — caching-proxy pathname replacement

Date: 2026-07-31  
Evidence class: `model-executed`  
Worker: H  
Linux source identity: `teamleaderleo/linux-fieldwork@ed49c01a85e9d363626db5d2973a33b67209e13b`  
Linux prepared evidence head: `dabe79cefb6062e20dc6201556b5f541a8470bbc`  
Local runtime: Python 3.13.5 on Linux

## In simple words

A local dependency-free reconstruction used the inspected imported proxy source, atomic-publication patch, and complete-stack composer replacements to generate the same request handler around the pathname operations under investigation. Real loopback requests and real rename/symlink operations reproduced the parent and final-component outcomes before hosted CI became available.

This is model evidence. The repository checkout, complete inherited matrix, workflow environment, and optimized child matrix remain owned by Linux Fieldwork CI run 677.

## Reconstruction boundary

The model used these inspected repository inputs:

- imported proxy blob `e57a8516a0c76167894b05fc56be0e3165535488`;
- complete composer implementation from Linux base `ed49c01a...`;
- atomic publication patch blob `4fe75d312ebb097f1b9d5fa27f9f6e8da61235c1`;
- the exact `HELPERS`, `REQUEST_SETUP`, and `FRESH_BLOCK` replacements;
- loopback binding replacement;
- Python compilation of the generated candidate.

The local reconstruction did not perform a Git checkout because the container could not resolve `github.com`. It did not execute the full repository test discovery or verify every retained patch artifact. Its value is the concrete filesystem and HTTP result for the exact generated pathname operations, not repository-gate coverage.

## Executed cases and retained results

| Case | HTTP | Returned bytes | Origin requests | Filesystem result |
| --- | --- | --- | ---: | --- |
| Old-cache parent renamed and replaced with outside symlink after validation | `200` | outside secret | 0 | outside object read and copied into new cache |
| Old-cache final object renamed and replaced with outside symlink after validation | `200` | outside secret | 0 | outside object read and copied into new cache |
| New-cache parent renamed and replaced with outside symlink before temporary creation | `200` | full origin payload | 1 | final object published in outside directory |
| New-cache final-name symlink inserted before temporary creation | `200` | full origin payload | 1 | symlink entry replaced by cache object; outside target unchanged |

Observed result tuple:

```text
old_parent = ([200], outside_body=True, origin=0, outside_copy=True)
old_final  = ([200], outside_body=True, origin=0, outside_copy=True)
pub_parent = ([200], payload_body=True, origin=1, outside_final=True)
pub_final  = ([200], payload_body=True, symlink_replaced=True,
              inside_payload=True, outside_target_unchanged=True)
```

## Interpretation

The model supports a component split:

- parent replacement redirects later descendant traversal for both reads and publication;
- final-component replacement redirects old-cache metadata/open operations;
- atomic publication replaces a final symlink entry instead of following its target.

This supports continuing toward an fd-relative descendant-path candidate after target execution. It does not yet authorize or select that candidate.

## Limits

- manual reconstruction from inspected source fragments;
- no complete repository checkout;
- no inherited seven-test composed matrix;
- no optimized-interpreter child execution in this model receipt;
- no measurement of natural race frequency, deployment exposure, or cross-user access;
- no public upstream interaction.
