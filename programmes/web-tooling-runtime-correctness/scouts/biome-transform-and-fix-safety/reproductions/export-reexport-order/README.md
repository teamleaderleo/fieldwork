# Safe re-export ordering changes module evaluation

## In simple words

Biome 2.5.6 classifies `organizeImports` as a safe assist. Applying `biome check --write` to this case moves a named re-export ahead of a star re-export. Both target modules have a visible top-level effect, so the output order changes.

## Revision

- `@biomejs/biome@2.5.6`
- Source: `biomejs/biome@d890b39c3ef21040bded453d9af91e1b301a0d67`

## Run

```sh
./reproduce.sh
```

Expected output:

```text
before=1:2:star,named
after=1:2:named,star
```

## Manual steps

```sh
cp index.before.mjs index.mjs
node consumer.mjs
npx -y @biomejs/biome@2.5.6 check index.mjs --write
node consumer.mjs
diff -u index.before.mjs index.mjs
```

Biome produces the same content as `index.after.mjs`.

## Boundary

The bindings keep the same values. The observable change is module evaluation order. No framework, bundler, test runner, or project configuration is involved.

Upstream contact authorized: `no`

Interaction performed: `none`
