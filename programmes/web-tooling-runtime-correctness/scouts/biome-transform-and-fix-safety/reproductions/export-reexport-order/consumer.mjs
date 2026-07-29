import { named, star } from "./index.mjs";

console.log(`${star}:${named}:${globalThis.order.join(",")}`);
