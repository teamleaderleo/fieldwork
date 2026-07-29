#!/usr/bin/env sh
set -eu

cp index.before.mjs index.mjs
before=$(node consumer.mjs)

npx -y @biomejs/biome@2.5.6 check index.mjs --write >/dev/null

after=$(node consumer.mjs)

printf 'before=%s\n' "$before"
printf 'after=%s\n' "$after"

test "$before" = '1:2:star,named'
test "$after" = '1:2:named,star'
cmp -s index.mjs index.after.mjs
