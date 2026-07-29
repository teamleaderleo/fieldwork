# Tailwind directive parser compatibility

## In simple words

Biome 2.5.6 rejects Tailwind `@apply` syntax under default CSS parser settings and formats the same file after `css.parser.tailwindDirectives` is enabled.

## Run

Default behaviour:

```sh
npx -y @biomejs/biome@2.5.6 format input.css
```

Expected: a diagnostic stating that Tailwind-specific syntax is disabled.

Configured behaviour:

```sh
npx -y @biomejs/biome@2.5.6 format input.css --config-path=biome.json
```

Expected: formatted CSS on stdout.

## Disposition

This is expected, actionable configuration behaviour retained as a migration and onboarding compatibility example.

Upstream contact authorized: `no`

Interaction performed: `none`
