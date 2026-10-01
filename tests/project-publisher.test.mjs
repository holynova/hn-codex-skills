import assert from "node:assert/strict";
import fs from "node:fs";
import os from "node:os";
import path from "node:path";
import { spawnSync } from "node:child_process";
import test from "node:test";
import { fileURLToPath } from "node:url";

const root = path.resolve(path.dirname(fileURLToPath(import.meta.url)), "..");
const validator = path.join(root, "skills/hn-project-publisher/scripts/validate_release_readme.mjs");
const repoUrl = "https://github.com/holynova/test-project";
const demoUrl = "https://test-project.xiaosang.cc/";
const pagesUrl = "https://holynova.github.io/test-project/";

function fixture(t, demo = demoUrl) {
  const dir = fs.mkdtempSync(path.join(os.tmpdir(), "hn-publisher-"));
  t.after(() => fs.rmSync(dir, { recursive: true, force: true }));
  fs.mkdirSync(path.join(dir, "assets"));
  // File-existence fixtures: this validator does not inspect image content.
  fs.writeFileSync(path.join(dir, "assets/screenshot.png"), "fixture");
  fs.writeFileSync(path.join(dir, "assets/qr.png"), "fixture");
  const readme = path.join(dir, "README.md");
  fs.writeFileSync(readme, `# 测试 / Test\n项目介绍。 A small demo.\n[Repo](${repoUrl})\n[Demo](${demo})\n![Screenshot](assets/screenshot.png)\n<img src="assets/qr.png" width="180">\n`);
  return { dir, readme };
}

function validate(readme, ...options) {
  return spawnSync(process.execPath, [validator, readme, repoUrl, demoUrl, ...options], { encoding: "utf8" });
}

test("Cloudflare-only README passes without a GitHub Pages URL", (t) => {
  const { readme } = fixture(t);
  const result = validate(readme, "500", "500");
  assert.equal(result.status, 0, result.stderr);
  assert.match(result.stdout, /online state and QR target are not checked/);
});

test("old Pages link does not satisfy the intended Cloudflare Demo", (t) => {
  const { readme } = fixture(t, pagesUrl);
  const result = validate(readme);
  assert.equal(result.status, 1);
  assert.match(result.stderr, /Demo URL is missing/);
});

test("missing screenshot or QR files block release validation", (t) => {
  for (const name of ["screenshot", "qr"]) {
    const { dir, readme } = fixture(t);
    fs.rmSync(path.join(dir, `assets/${name}.png`));
    const result = validate(readme);
    assert.equal(result.status, 1);
    assert.match(result.stderr, /file does not exist/);
  }
});

test("explicit additional URL remains required for legacy dual-platform calls", (t) => {
  const { readme } = fixture(t, pagesUrl);
  const args = [validator, readme, repoUrl, pagesUrl, "500", "500", demoUrl];
  let result = spawnSync(process.execPath, args, { encoding: "utf8" });
  assert.equal(result.status, 1);
  assert.match(result.stderr, /Additional public URL is missing/);
  fs.appendFileSync(readme, `\n[Cloudflare](${demoUrl})\n`);
  result = spawnSync(process.execPath, args, { encoding: "utf8" });
  assert.equal(result.status, 0, result.stderr);
});

test("Chinese and English length limits still block oversized README text", (t) => {
  for (const prose of ["中".repeat(501), "word ".repeat(501)]) {
    const { readme } = fixture(t);
    fs.appendFileSync(readme, prose);
    const result = validate(readme, "500", "500");
    assert.equal(result.status, 1);
    assert.match(result.stderr, /maximum is 500/);
  }
});
