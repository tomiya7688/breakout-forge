import fs from "node:fs";
import path from "node:path";
import { CopilotClient } from "@github/copilot-sdk";

const imagesDir = path.resolve(process.argv[2]);
const outputPath = path.resolve(process.argv[3]);
const model = process.env.UI_REVIEW_MODEL;
const reviewer = process.env.UI_REVIEW_NAME;
const rubric = process.env.UI_REVIEW_RUBRIC;

if (!model || !reviewer || !rubric) {
  throw new Error("UI_REVIEW_MODEL, UI_REVIEW_NAME and UI_REVIEW_RUBRIC are required");
}

const files = fs.readdirSync(imagesDir)
  .filter((name) => name.endsWith(".png"))
  .sort();

if (files.length !== 9) {
  throw new Error(`expected 9 UI screenshots, got ${files.length}`);
}

const prompt = `
You are ${reviewer}, an independent release UI reviewer for Breakout Forge.
Review all nine attached screenshots as one state sequence.

Rubric:
${rubric}

Return ONLY one JSON object with exactly this shape:
{
  "reviewer": "${reviewer}",
  "model": "${model}",
  "status": "approved" | "rejected",
  "release_blockers": ["..."],
  "must_fix": ["..."],
  "known_issues": ["..."],
  "observations": ["..."]
}

Rules:
- A release_blocker means launch/gameplay/state comprehension is materially broken.
- must_fix means a high-frequency serious UI defect that should block v1.0.0.
- known_issues are non-blocking observations.
- Do not invent interactions not visible in the screenshots.
- If there are no blockers/must-fix issues, status must be "approved".
`.trim();

const attachments = files.map((name) => ({
  type: "file",
  path: path.join(imagesDir, name),
  displayName: name,
}));

const client = new CopilotClient();
await client.start();
try {
  const session = await client.createSession({ model });
  const response = await session.sendAndWait({ prompt, attachments });
  const content = response?.data?.content ?? "";
  const start = content.indexOf("{");
  const end = content.lastIndexOf("}");
  if (start < 0 || end < start) {
    throw new Error(`model did not return JSON: ${content}`);
  }
  const result = JSON.parse(content.slice(start, end + 1));
  result.files = files;
  fs.writeFileSync(outputPath, JSON.stringify(result, null, 2) + "\n", "utf8");

  if (result.status !== "approved") {
    throw new Error(`${reviewer} rejected UI review`);
  }
  if ((result.release_blockers ?? []).length || (result.must_fix ?? []).length) {
    throw new Error(`${reviewer} reported blocking UI findings`);
  }
} finally {
  await client.stop();
}
