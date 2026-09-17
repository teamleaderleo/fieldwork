// Fieldwork #709 reference loader.
// Executed with Node v22.16.0.
// Run with a module that imports both spellings:
// node --experimental-loader ./builtin-loader-hook-node.mjs ./import-both.mjs

export async function resolve(specifier, context, nextResolve) {
  if (specifier === "http" || specifier === "node:http") {
    console.log(`HOOK ${JSON.stringify(specifier)}`);
  }
  return nextResolve(specifier, context);
}
