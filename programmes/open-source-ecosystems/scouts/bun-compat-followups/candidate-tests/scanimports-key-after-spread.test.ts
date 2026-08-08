import { expect, test } from "bun:test";

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

test("scanImports reports bare JSX package for key-after-spread fallback", () => {
  const result = paths('export default <div {...obj} key="after" />;');
  const expected = [["import-statement", "react"]];
  expect(result.scanImports).toEqual(expected);
  expect(result.scan).toEqual(expected);
});

test("scanImports keeps automatic runtime dependency for normal JSX", () => {
  const result = paths("export default <div />;");
  const expected = [["import-statement", "react/jsx-dev-runtime"]];
  expect(result.scanImports).toEqual(expected);
  expect(result.scan).toEqual(expected);
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

test("scanImports uses the custom JSX package for the fallback", () => {
  const opts = {
    loader: "tsx" as const,
    tsconfig: { compilerOptions: { jsx: "react-jsx" as const, jsxImportSource: "preact" } },
    logLevel: "error" as const,
  };
  const result = paths('export default <div {...obj} key="after" />;', opts);
  const expected = [["import-statement", "preact"]];
  expect(result.scanImports).toEqual(expected);
  expect(result.scan).toEqual(expected);
});

test("autoImportJSX false still suppresses injected scan records", () => {
  const result = paths('export default <div {...obj} key="after" />;', { ...dev, autoImportJSX: false });
  expect(result.scanImports).toEqual([]);
  expect(result.scan).toEqual([]);
});
