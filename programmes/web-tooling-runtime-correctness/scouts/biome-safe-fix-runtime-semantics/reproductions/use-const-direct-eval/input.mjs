function run() {
  let value = 1;
  let outcome;

  try {
    eval("value = 2");
    outcome = { status: "completed", value };
  } catch (error) {
    outcome = {
      status: "threw",
      name: error?.name ?? null,
      message: error?.message ?? String(error),
      value,
    };
  }

  return outcome;
}

console.log(JSON.stringify(run()));
