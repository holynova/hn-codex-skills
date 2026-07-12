#!/usr/bin/env node

import fs from "node:fs";
import path from "node:path";
import process from "node:process";

function usage() {
  console.error("Usage: validate_release_version.mjs <package.json> <page-file-or-build-dir> [previous-version]");
  process.exit(2);
}

function parseVersion(value, label) {
  const match = String(value).match(/^(?:v)?(0|[1-9]\d*)\.(0|[1-9]\d*)\.(0|[1-9]\d*)(?:-([0-9A-Za-z.-]+))?(?:\+[0-9A-Za-z.-]+)?$/);
  if (!match) throw new Error(`${label} is not a valid semantic version: ${value}`);
  return {
    raw: String(value).replace(/^v/, ""),
    core: match.slice(1, 4).map(Number),
    prerelease: match[4]?.split(".") || [],
  };
}

function compareIdentifiers(left, right) {
  const leftNumber = /^\d+$/.test(left) ? Number(left) : null;
  const rightNumber = /^\d+$/.test(right) ? Number(right) : null;
  if (leftNumber !== null && rightNumber !== null) return Math.sign(leftNumber - rightNumber);
  if (leftNumber !== null) return -1;
  if (rightNumber !== null) return 1;
  return left.localeCompare(right);
}

function compareVersions(left, right) {
  for (let index = 0; index < 3; index += 1) {
    if (left.core[index] !== right.core[index]) return Math.sign(left.core[index] - right.core[index]);
  }
  if (!left.prerelease.length && !right.prerelease.length) return 0;
  if (!left.prerelease.length) return 1;
  if (!right.prerelease.length) return -1;
  const length = Math.max(left.prerelease.length, right.prerelease.length);
  for (let index = 0; index < length; index += 1) {
    if (left.prerelease[index] === undefined) return -1;
    if (right.prerelease[index] === undefined) return 1;
    const result = compareIdentifiers(left.prerelease[index], right.prerelease[index]);
    if (result) return result;
  }
  return 0;
}

function collectTextFiles(target) {
  const stat = fs.statSync(target);
  if (stat.isFile()) return [target];
  if (!stat.isDirectory()) return [];
  const allowed = new Set([".html", ".js", ".mjs", ".cjs", ".css", ".json", ".txt"]);
  return fs.readdirSync(target, { withFileTypes: true }).flatMap((entry) => {
    const child = path.join(target, entry.name);
    if (entry.isDirectory()) return collectTextFiles(child);
    return entry.isFile() && allowed.has(path.extname(entry.name).toLowerCase()) ? [child] : [];
  });
}

const [, , packageArg, pageArg, previousArg] = process.argv;
if (!packageArg || !pageArg) usage();

const packagePath = path.resolve(packageArg);
const pagePath = path.resolve(pageArg);
const packageJson = JSON.parse(fs.readFileSync(packagePath, "utf8"));
const current = parseVersion(packageJson.version, "package.json version");

if (previousArg) {
  const previous = parseVersion(previousArg, "previous version");
  if (compareVersions(current, previous) <= 0) {
    throw new Error(`Version did not increase: ${previous.raw} -> ${current.raw}`);
  }
}

const marker = `v${current.raw}`;
const files = collectTextFiles(pagePath);
const matches = files.filter((file) => fs.readFileSync(file, "utf8").includes(marker));
if (!matches.length) {
  throw new Error(`Deployable page does not contain the visible-version marker ${marker}: ${pagePath}`);
}

console.log(`Version validation passed: ${previousArg ? `${previousArg} -> ` : ""}${current.raw}; ${marker} found in ${matches.length} deployable file(s).`);
