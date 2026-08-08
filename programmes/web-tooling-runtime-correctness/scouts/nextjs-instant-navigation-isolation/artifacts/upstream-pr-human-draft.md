# `fix(next-playwright): scope instant cookie cleanup to app URL`

Fixes #[issue]

## What

`instant()` sets its testing cookie for one application hostname, but cleanup currently searches the entire Playwright `BrowserContext` for cookies with the same name.

This changes cleanup from:

```ts
context.cookies()
```

to:

```ts
context.cookies(scopeURL)
```

so it only expires testing cookies that apply to the application URL being controlled.

## Why

If the browser context also contains a `next-instant-navigation-testing` cookie for another origin, calling `instant()` for app A can currently delete app B’s cookie.

Using Playwright’s URL-filtered cookie lookup keeps the existing cookie domain/path behavior while avoiding cleanup of cookies that don’t apply to app A.

## Tests

Added coverage to the existing Instant Navigation testing suite verifying that another origin’s testing cookie survives both entering and leaving an `instant()` scope.
