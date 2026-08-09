# Campaign 0745: Tauri resource target collision

State: `claimed`

Issue: #745  
Parent scout: #118  
Target source: `34ec18ba5e1acabebd66ae79d6fc746f63d8eb96`  
Claim scope: `mechanism`  
Upstream contact authorized: `false`

## In simple words

Tauri derives each mapped resource destination independently and copies it immediately. Two distinct source entries can resolve to one exact target and the later `fs::copy` can silently replace the earlier file. There is no uniqueness pass before copying.

## Question

Does an exact duplicate bundle-resource target silently overwrite another source, and can Tauri reject such ambiguity before any destination is written?

## Current evidence

- `source-established`: `ResourcePaths::from_map` iterates a `HashMap`; `resource_from_path` computes targets independently; `copy_resources` writes each target immediately; `copy_file` uses `fs::copy`.
- `target-test-prepared`: exact-target collision regression retained in #721.

## Next discriminator

Execute two distinct sources targeting `same.txt`, with distinct-target and repeat-order controls. If reproduced, compare resolve-all-and-validate-before-copy against current valid resource behavior.

## Stop conditions

Stop with target-executed reproduction/repair or a negative result showing an earlier validation layer rejects the collision. Case folding, Unicode aliases, symlink aliases, and installer rewrites remain out of scope until the exact case is established.