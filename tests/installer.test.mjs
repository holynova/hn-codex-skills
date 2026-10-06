import assert from "node:assert/strict";
import fs from "node:fs";
import os from "node:os";
import path from "node:path";
import { spawnSync } from "node:child_process";
import test from "node:test";
import { fileURLToPath } from "node:url";

const repoRoot = path.resolve(path.dirname(fileURLToPath(import.meta.url)), "..");
const installer = path.join(repoRoot, "bin", "install.mjs");

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
  assert.equal(installed.length, 15);
  for (const entry of installed) {
    assert.ok(fs.existsSync(path.join(target, entry.name, "SKILL.md")));
    assert.ok(fs.existsSync(path.join(target, entry.name, "agents", "openai.yaml")));
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
