import assert from "node:assert/strict";
import fs from "node:fs";
import os from "node:os";
import path from "node:path";
import { spawnSync } from "node:child_process";
import test from "node:test";
import { createHash } from "node:crypto";
import { fileURLToPath } from "node:url";

const repoRoot = path.resolve(path.dirname(fileURLToPath(import.meta.url)), "..");
const installer = path.join(repoRoot, "bin", "install.mjs");

test("pen-art installation preserves all mandatory images and references", () => withTempDir((temp) => {
  const name = "hn-flowing-pen-art";
  const result = runInstaller(["install", name, "--path", temp]);
  assert.equal(result.status, 0, result.stderr);
  const files = [
    "SKILL.md", "agents/openai.yaml", "references/examples.md", "references/prompts.md",
    ...["01-tide-keeper", "02-moth-dreamer", "03-white-stag", "04-spiral-city", "05-shell-atlas"]
      .map((stem) => `references/images/${stem}.webp`),
  ];
  for (const file of files) {
    const source = fs.readFileSync(path.join(repoRoot, "skills", name, file));
    const installed = fs.readFileSync(path.join(temp, name, file));
    assert.equal(createHash("sha256").update(installed).digest("hex"),
      createHash("sha256").update(source).digest("hex"), file);
    if (file.endsWith(".webp")) {
      assert.equal(installed.toString("ascii", 0, 4), "RIFF", file);
      assert.equal(installed.toString("ascii", 8, 12), "WEBP", file);
    }
  }
}));

function runInstaller(args) {
  return spawnSync(process.execPath, [installer, ...args], {
    cwd: repoRoot,
    encoding: "utf8",
  });
}

function withTempDir(callback) {
  const temp = fs.mkdtempSync(path.join(os.tmpdir(), "hn-skills-installer-"));
  try {
    return callback(temp);
  } finally {
    fs.rmSync(temp, { recursive: true, force: true });
  }
}

test("installs every bundled skill into an isolated directory", () => withTempDir((temp) => {
  const target = path.join(temp, "skills");
  const result = runInstaller(["install", "--path", target]);
  assert.equal(result.status, 0, result.stderr);
  const installed = fs.readdirSync(target, { withFileTypes: true })
    .filter((entry) => entry.isDirectory() && !entry.name.startsWith("."));
  assert.equal(installed.length, 19);
  for (const entry of installed) {
    assert.ok(fs.existsSync(path.join(target, entry.name, "SKILL.md")));
    assert.ok(fs.existsSync(path.join(target, entry.name, "agents", "openai.yaml")));
  }
}));

test("installs twilight anime art with all five required visual references intact", () => withTempDir((temp) => {
  const target = path.join(temp, "skills");
  const result = runInstaller(["install", "twilight-anime-art", "--path", target]);
  assert.equal(result.status, 0, result.stderr);
  assert.deepEqual(fs.readdirSync(target), ["twilight-anime-art"]);
  for (const name of ["01-cafe", "02-train", "03-bookstore", "04-lodge", "05-rooftop"]) {
    const relative = path.join("references", "images", `${name}.webp`);
    const original = fs.readFileSync(path.join(repoRoot, "skills", "twilight-anime-art", relative));
    const installed = fs.readFileSync(path.join(target, "twilight-anime-art", relative));
    assert.equal(original.subarray(0, 4).toString(), "RIFF");
    assert.equal(original.subarray(8, 12).toString(), "WEBP");
    assert.ok(original.length > 1000);
    assert.deepEqual(installed, original);
  }
}));

test("preflights all conflicts before installing any skill", () => withTempDir((temp) => {
  const target = path.join(temp, "skills");
  const conflict = path.join(target, "hn-project-publisher");
  fs.mkdirSync(conflict, { recursive: true });
  fs.writeFileSync(path.join(conflict, "user-marker.txt"), "preserve me");

  const result = runInstaller(["install", "--path", target]);
  assert.notEqual(result.status, 0);
  assert.match(result.stderr, /Target already exists/);
  assert.equal(fs.readFileSync(path.join(conflict, "user-marker.txt"), "utf8"), "preserve me");
  assert.equal(fs.existsSync(path.join(target, "hn-windows-stability-doctor")), false);
}));

test("force replacement leaves no staging or backup directories", () => withTempDir((temp) => {
  const target = path.join(temp, "skills");
  const existing = path.join(target, "hn-tool-ui-polisher");
  fs.mkdirSync(existing, { recursive: true });
  fs.writeFileSync(path.join(existing, "user-marker.txt"), "old copy");

  const result = runInstaller([
    "install", "hn-tool-ui-polisher", "--path", target, "--force",
  ]);
  assert.equal(result.status, 0, result.stderr);
  assert.equal(fs.existsSync(path.join(existing, "user-marker.txt")), false);
  assert.ok(fs.existsSync(path.join(existing, "SKILL.md")));
  assert.deepEqual(fs.readdirSync(target).filter((name) => name.startsWith(".")), []);
}));

test("prevents installing archived skills in backup directory", () => withTempDir((temp) => {
  const target = path.join(temp, "skills");
  const archivedSkills = [
    "hn-frontend-project-shipper",
    "hn-agent-workflow-productizer",
    "hn-data-to-github-pages-gallery",
    "hn-github-works",
    "hn-opencli-batch-image-production",
    "hn-stateful-cron-report-pipeline",
  ];
  for (const skill of archivedSkills) {
    const result = runInstaller(["install", skill, "--path", target]);
    assert.notEqual(result.status, 0);
    assert.match(result.stderr, /Unknown skill/);
  }
}));

// The visual reference library is required runtime input, not optional documentation.
test("installs ink dance sketch with all required visual references intact", () => withTempDir((temp) => {
  const target = path.join(temp, "skills");
  const name = "hn-ink-dance-sketch";
  const result = runInstaller(["install", name, "--path", target]);
  assert.equal(result.status, 0, result.stderr);
  const files = [
    "references/examples.md", "references/prompting.md",
    ...["01-ink-ribbon", "02-ballet", "03-flamenco", "04-mongolian",
      "05-bharatanatyam", "06-contemporary"].map((file) => `references/examples/${file}.webp`),
  ];
  for (const file of files) {
    const source = fs.readFileSync(path.join(repoRoot, "skills", name, file));
    const installed = fs.readFileSync(path.join(target, name, file));
    assert.deepEqual(installed, source, `Required reference changed or missing: ${file}`);
    if (file.endsWith(".webp")) {
      assert.equal(installed.toString("ascii", 0, 4), "RIFF");
      assert.equal(installed.toString("ascii", 8, 12), "WEBP");
    }
  }
}));

test("woodcut installation preserves every mandatory visual reference", () => withTempDir((temp) => {
  const result = runInstaller(["install", "hn-color-woodcut", "--path", temp]);
  assert.equal(result.status, 0, result.stderr);
  const source = path.join(repoRoot, "skills", "hn-color-woodcut", "references");
  const installed = path.join(temp, "hn-color-woodcut", "references");
  const examples = JSON.parse(fs.readFileSync(path.join(installed, "examples.json"), "utf8"));
  assert.equal(examples.length, 8);
  for (const example of examples) {
    const image = fs.readFileSync(path.join(installed, example.file));
    assert.ok(image.length > 1000, example.file);
    assert.equal(image.subarray(0, 4).toString(), "RIFF", example.file);
    assert.equal(image.subarray(8, 12).toString(), "WEBP", example.file);
    assert.deepEqual(image, fs.readFileSync(path.join(source, example.file)), example.file);
  }
  assert.deepEqual(fs.readFileSync(path.join(installed, "examples-board.jpg")), fs.readFileSync(path.join(source, "examples-board.jpg")));
}));

test("installs required translucent toy example images with matching hashes", () => withTempDir((temp) => {
  const target = path.join(temp, "skills");
  const result = runInstaller(["install", "hn-translucent-toy", "--path", target]);
  assert.equal(result.status, 0, result.stderr);
  const root = path.join(target, "hn-translucent-toy");
  const manifest = JSON.parse(fs.readFileSync(path.join(root, "references", "examples.json"), "utf8"));
  assert.equal(manifest.required, true);
  assert.equal(manifest.examples.length, 6);
  assert.equal(manifest.examples.filter((example) => example.role === "foundation").length, 3);
  for (const example of manifest.examples) {
    const image = path.resolve(root, example.image);
    assert.ok(image.startsWith(`${root}${path.sep}`));
    const bytes = fs.readFileSync(image);
    assert.equal(bytes.subarray(0, 4).toString(), "RIFF");
    assert.equal(bytes.subarray(8, 12).toString(), "WEBP");
    assert.equal(createHash("sha256").update(bytes).digest("hex"), example.sha256);
    assert.deepEqual(bytes, fs.readFileSync(path.join(repoRoot, "skills", "hn-translucent-toy", example.image)));
  }
}));
