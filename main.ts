// main.ts — copy the rendered treasure map to /output/entry.png.
// Entry for make.fun bounty "Charm the Cartographers: A One Day
// Treasure Map Sprint" (u-ravendell-charm-the-cartographers-a-one-day-00854547).
// Node 22, stdlib only. The image itself is produced by
// tools/make-image.py (Python 3 stdlib + PIL, fixed seed 42, fully
// procedural — parchment, island, river, dashed route, compass rose,
// sea monster and ship are all drawn in code, no network or assets);
// this script only places the finished PNG where the gate expects it.
import { copyFileSync, mkdirSync } from "node:fs";
import { dirname, join } from "node:path";
import { fileURLToPath } from "node:url";

const here = dirname(fileURLToPath(import.meta.url));
const src = join(here, "entry.png");
const dest = "/output/entry.png";

mkdirSync("/output", { recursive: true });
copyFileSync(src, dest);
console.log(`copied ${src} -> ${dest}`);
