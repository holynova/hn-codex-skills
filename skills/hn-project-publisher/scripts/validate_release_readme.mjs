#!/usr/bin/env node

import fs from "node:fs";
import path from "node:path";
import process from "node:process";

function usage() {
  console.error("Usage: validate_release_readme.mjs <README> <repo-url> <pages-url> [max-units]");
  process.exit(2);
}

const [, , readmeArg, repoUrl, pagesUrl, maxArg = "200"] = process.argv;
if (!readmeArg || !repoUrl || !pagesUrl) usage();

const maxUnits = Number.parseInt(maxArg, 10);
if (!Number.isInteger(maxUnits) || maxUnits < 1) {
  throw new Error(`Invalid max-units: ${maxArg}`);
}

const readmePath = path.resolve(readmeArg);
const markdown = fs.readFileSync(readmePath, "utf8");
const relativeImageMatch = markdown.match(/!\[[^\]]+\]\(((?!https?:\/\/)[^)]+)\)/);
const imageDestination = relativeImageMatch?.[1]
  ?.trim()
  .replace(/^<|>$/g, "")
  .split(/[?#]/, 1)[0];
const imagePath = imageDestination
  ? path.resolve(path.dirname(readmePath), decodeURIComponent(imageDestination))
  : null;

const withoutCode = markdown.replace(/```[\s\S]*?```/g, " ");
const withoutImages = withoutCode.replace(/!\[[^\]]*\]\([^)]*\)/g, " ");
const withoutDestinations = withoutImages
  .replace(/\[([^\]]+)\]\([^)]*\)/g, "$1")
  .replace(/https?:\/\/\S+/g, " ")
  .replace(/<[^>]+>/g, " ");
const hanCount = (withoutDestinations.match(/\p{Script=Han}/gu) || []).length;
const nonHan = withoutDestinations.replace(/\p{Script=Han}/gu, " ");
const englishWordCount = (nonHan.match(/[\p{L}\p{N}]+(?:['’-][\p{L}\p{N}]+)*/gu) || []).length;
const units = hanCount + englishWordCount;

const checks = [
  [markdown.includes(repoUrl), `repository URL is missing: ${repoUrl}`],
  [markdown.includes(pagesUrl), `Pages URL is missing: ${pagesUrl}`],
  [Boolean(imagePath), "a repository-relative screenshot is missing"],
  [Boolean(imagePath && fs.existsSync(imagePath)), `screenshot file does not exist: ${imagePath || "unknown"}`],
  [units <= maxUnits, `README text is ${units} units; maximum is ${maxUnits}`],
];

const failures = checks.filter(([ok]) => !ok).map(([, message]) => message);
if (failures.length) {
  console.error(`README validation failed for ${readmePath}:`);
  for (const failure of failures) console.error(`- ${failure}`);
  process.exit(1);
}

console.log(`README validation passed: ${units}/${maxUnits} text units, screenshot and public links present.`);
