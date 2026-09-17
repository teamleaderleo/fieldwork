const speciesReads = [];

class FinalArray extends Array {}

class IntermediateArray extends Array {
  static get [Symbol.species]() {
    speciesReads.push("IntermediateArray");
    return FinalArray;
  }
}

class SourceArray extends Array {
  static get [Symbol.species]() {
    speciesReads.push("SourceArray");
    return IntermediateArray;
  }
}

const source = new SourceArray(1, 2);
const result = source.map((value) => [value]).flat();

console.log(
  JSON.stringify({
    constructor: result.constructor.name,
    speciesReads,
    values: [...result],
  }),
);
