const args = [3];
const result = Array(...args);

console.log(
  JSON.stringify({
    length: result.length,
    keys: Object.keys(result),
    hasIndexZero: 0 in result,
    first: result[0] ?? null,
  }),
);
