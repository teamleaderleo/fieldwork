import { expect, test } from "bun:test";

// Fieldwork-owned candidate regression for oven-sh/bun#35557 follow-up.
// Evidence: target-test-prepared. This file has NOT been executed on Bun.

const dev = {
  loader: "tsx" as const,
  define: { "process.env.NODE_ENV": JSON.stringify("development") },
  logLevel: "error" as const,
};

function paths(src: string, opts: any = dev) {
  const t = new Bun.Transpiler(opts);
  return {
    scanImports: t.scanImports(src).map(x => [x.kind, x.path]),
    scan: t.scan(src).imports.map(x => [x.kind, x.path]),
  };
}

function expectBoth(result: ReturnType<typeof paths>, expected: string[][]) {
  expect(result.scanImports).toEqual(expected);
  expect(result.scan).toEqual(expected);
}

test("scanImports reports bare JSX package for key-after-spread fallback", () => {
  expectBoth(paths('export default <div {...obj} key="after" />;'), [["import-statement", "react"]]);
});

test("scanImports keeps automatic runtime dependency for normal JSX", () => {
  expectBoth(paths("export default <div />;"), [["import-statement", "react/jsx-dev-runtime"]]);
});

test("scanImports keeps automatic runtime dependency for fragments", () => {
  expectBoth(paths("export default <><div /></>;"), [["import-statement", "react/jsx-dev-runtime"]]);
});

test("scanImports reports both dependencies in a mixed file", () => {
  const result = paths(`
    export const normal = <span />;
    export const fallback = <div {...obj} key="after" />;
  `);

  for (const list of [result.scanImports, result.scan]) {
    expect(new Set(list.map(([, path]) => path))).toEqual(new Set(["react/jsx-dev-runtime", "react"]));
  }
});

test("scanImports reports both dependencies when normal JSX is nested in a fallback", () => {
  const result = paths('export default <div {...obj} key="after"><span /></div>;');

  for (const list of [result.scanImports, result.scan]) {
    expect(new Set(list.map(([, path]) => path))).toEqual(new Set(["react/jsx-dev-runtime", "react"]));
  }
});

test("scanImports uses the custom JSX package for the fallback", () => {
  const opts = {
    loader: "tsx" as const,
    tsconfig: { compilerOptions: { jsx: "react-jsx" as const, jsxImportSource: "preact" } },
    logLevel: "error" as const,
  };
  expectBoth(paths('export default <div {...obj} key="after" />;', opts), [["import-statement", "preact"]]);
});

test("@jsxImportSource also controls the fallback bare package", () => {
  expectBoth(paths('/** @jsxImportSource preact */\nexport default <div {...obj} key="after" />;'), [
    ["import-statement", "preact"],
  ]);
});

test("@jsxRuntime automatic over classic config still classifies the fallback", () => {
  const opts = {
    ...dev,
    tsconfig: { compilerOptions: { jsx: "react" as const } },
  };
  expectBoth(paths('// @jsxRuntime automatic\nexport default <div {...obj} key="after" />;', opts), [
    ["import-statement", "react"],
  ]);
});

test("@jsxRuntime classic over automatic suppresses scan-time auto imports", () => {
  expectBoth(paths('// @jsxRuntime classic\nexport default <div {...obj} key="after" />;'), []);
});

test("autoImportJSX false still suppresses injected scan records", () => {
  expectBoth(paths('export default <div {...obj} key="after" />;', { ...dev, autoImportJSX: false }), []);
});
