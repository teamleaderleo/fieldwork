// Fieldwork #709 reference control.
// Executed with Node v22.16.0.
// Run: node builtin-specifier-node.mjs

import Module from "node:module";

console.log(
  JSON.stringify(
    {
      node: process.version,
      importMetaResolveBare: import.meta.resolve("http"),
      importMetaResolvePrefixed: import.meta.resolve("node:http"),
      isBuiltinBare: Module.isBuiltin("http"),
      isBuiltinPrefixed: Module.isBuiltin("node:http"),
    },
    null,
    2,
  ),
);

// CommonJS control, run separately:
// node -e 'console.log({ bare: require.resolve("http"), prefixed: require.resolve("node:http"), same: require("http") === require("node:http") })'
