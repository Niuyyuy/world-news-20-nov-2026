// World news in one image, Friday 20 November 2026.
// Front page: Cyclone Akvan hits Odisha, Russia pounds Kyiv
// overnight, Asian markets slump, Samsung names a new mobile
// chief, Sydney terror raids, and Cyclone Xavier tracked.
// The image is drawn in the style of a printed newspaper front
// page: masthead, dateline, and six illustrated stories.
// This program ships the finished front page beside it and writes
// exactly those bytes to the grader's output folder, every run.
// It uses only the Node standard library, reads no network, and
// writes nothing else, so two runs produce identical output.

import { readFileSync, writeFileSync, mkdirSync } from "node:fs";
import { dirname, join } from "node:path";
import { fileURLToPath } from "node:url";

const here = dirname(fileURLToPath(import.meta.url));
const source = join(here, "entry.png");
const outputDir = process.env.MAKEFUN_OUTPUT_DIR ?? "/output";
const target = join(outputDir, "entry.png");

mkdirSync(outputDir, { recursive: true });
const bytes = readFileSync(source);
// The competition gate allows at most 1 MiB; fail loudly here
// rather than submitting a file the gate would refuse.
if (bytes.length > 1048576) {
  throw new Error(`entry.png is ${bytes.length} bytes, over the 1 MiB limit`);
}
writeFileSync(target, bytes);
console.log(`wrote ${target} (${bytes.length} bytes)`);
