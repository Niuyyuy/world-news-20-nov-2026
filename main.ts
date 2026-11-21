// Front page for Friday 20 November 2026: the Kyiv barrage, Cyclone
// Akvan's landfall, a seventh day of market slides, the Red Sea
// escalation, the Haiti gang raid, and the Sydney terror raids.
// The page itself is drawn by frontpage.py and shipped beside this
// program as entry.png; this program copies those exact bytes to the
// output directory the grader provides. It touches no network and
// uses no randomness, so every run writes identical bytes.

import { mkdirSync, readFileSync, writeFileSync } from "node:fs";
import { dirname, join } from "node:path";
import { fileURLToPath } from "node:url";

const LIMIT = 1048576; // 1 MiB, the competition gate
const here = dirname(fileURLToPath(import.meta.url));
const picture = readFileSync(join(here, "entry.png"));
if (picture.length > LIMIT) {
  throw new Error(`entry.png is ${picture.length} bytes, above the ${LIMIT} limit`);
}
const outDir = process.env.MAKEFUN_OUTPUT_DIR ?? "/output";
mkdirSync(outDir, { recursive: true });
// The grader reads exactly one file from the output directory, so
// the name stays entry.png whatever the directory is called.
const dest = join(outDir, "entry.png");
writeFileSync(dest, picture);
console.log(`wrote ${dest} (${picture.length} bytes)`);
