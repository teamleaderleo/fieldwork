let calls = 0;

function effect(value) {
  calls++;
  return value;
}

const orResult = effect(false) || true;
const andResult = effect(true) && false;
const truthyAnd = "value" && true;
const falsyOr = 0 || false;

console.log(
  JSON.stringify({ calls, orResult, andResult, truthyAnd, falsyOr }),
);
