function targetSetterCase() {
  let calls = 0;
  const result = Object.assign(
    {
      set value(next) {
        calls += next;
      },
    },
    { value: 2 },
  );
  const descriptor = Object.getOwnPropertyDescriptor(result, "value");
  return {
    calls,
    propertyKind: descriptor?.set ? "accessor" : "data",
    value: descriptor?.set ? null : result.value,
  };
}

function sourceGetterCase() {
  let reads = 0;
  const result = Object.assign(
    {},
    {
      get value() {
        reads++;
        return 7;
      },
    },
  );
  const descriptor = Object.getOwnPropertyDescriptor(result, "value");
  const readsBeforeValue = reads;
  const value = result.value;
  return {
    readsBeforeValue,
    readsAfterValue: reads,
    propertyKind: descriptor?.get ? "accessor" : "data",
    value,
  };
}

console.log(
  JSON.stringify({
    targetSetter: targetSetterCase(),
    sourceGetter: sourceGetterCase(),
  }),
);
