#!/usr/bin/env node

import fs from "node:fs";
import path from "node:path";
import process from "node:process";
import { spawnSync } from "node:child_process";
import { fileURLToPath } from "node:url";

function usage() {
  console.error("Usage: validate_release_readme.mjs <README> <repo-url> <demo-url> [max-han] [max-english] [additional-url] [--companion FILE] [--screenshot FILE] [--preserve-length]");
  process.exit(2);
}

const args = process.argv.slice(2);
const options = {};
for (let i = 0; i < args.length;) {
  if (args[i] === "--preserve-length") {
    options.preserveLength = true;
    args.splice(i, 1);
  } else if (["--companion", "--screenshot"].includes(args[i])) {
    if (!args[i + 1] || args[i + 1].startsWith("--")) usage();
    options[args[i].slice(2)] = args[i + 1];
    args.splice(i, 2);
  } else if (args[i].startsWith("--")) {
    usage();
  } else i++;
}
const [readmeArg, repoUrl, demoUrl, arg4, arg5, arg6] = args;
if (!readmeArg || !repoUrl || !demoUrl) usage();

let maxHan = 500;
let maxEnglish = 500;
let additionalUrl = "";

if (arg4) {
  if (/^https?:\/\//i.test(arg4) || arg4.includes(".xiaosang.cc")) {
    additionalUrl = arg4;
  } else {
    const num = Number.parseInt(arg4, 10);
    if (Number.isInteger(num) && num > 0) {
      maxHan = num;
      maxEnglish = num;
    }
  }
}

if (arg5) {
  if (/^https?:\/\//i.test(arg5) || arg5.includes(".xiaosang.cc")) {
    additionalUrl = arg5;
  } else {
    const num = Number.parseInt(arg5, 10);
    if (Number.isInteger(num) && num > 0) {
      maxEnglish = num;
    }
  }
}

if (arg6) {
  additionalUrl = arg6;
}

const readmePath = path.resolve(readmeArg);
if (!fs.existsSync(readmePath)) {
  console.error(`Error: README file not found at ${readmePath}`);
  process.exit(1);
}

const markdown = fs.readFileSync(readmePath, "utf8");
const companionPath = options.companion ? path.resolve(options.companion) : null;
if (companionPath && (!fs.existsSync(companionPath) || companionPath === readmePath)) {
  console.error("Companion README must exist and differ from the primary README.");
  process.exit(1);
}
const companion = companionPath ? fs.readFileSync(companionPath, "utf8") : "";
function linksTo(source, from, target) {
  return [...source.matchAll(/(?<!!)\[[^\]]*\]\(([^)]+)\)|<a\s+[^>]*href=["']([^"']+)["']/gi)].some(m => {
    const dest = cleanDest(m[1] || m[2]);
    if (!dest || /^[a-z]+:/i.test(dest)) return false;
    try { return path.resolve(path.dirname(from), decodeURIComponent(dest)) === target; }
    catch { return false; }
  });
}

// Extract all image paths (both Markdown and HTML img tags)
const mdImageMatches = [...markdown.matchAll(/!\[([^\]]*)\]\(((?!https?:\/\/)[^)]+)\)/g)];
const htmlImageMatches = [...markdown.matchAll(/<img\s+[^>]*?src=["']((?!https?:\/\/)[^"']+)["'][^>]*>/gi)];

function cleanDest(dest) {
  return dest?.trim().replace(/^<|>$/g, "").split(/[?#]/, 1)[0];
}

const allLocalImages = [
  ...mdImageMatches.map(m => ({ alt: m[1] || "", dest: cleanDest(m[2]) })),
  ...htmlImageMatches.map(m => ({ alt: m[0].match(/alt=["']([^"']*)["']/i)?.[1] || "", dest: cleanDest(m[1]) })),
];

// Detect screenshot vs QR code
const qrImages = allLocalImages.filter(img =>
  /(qr|qrcode|扫码)/i.test(img.dest) || /(qr|qrcode|扫码)/i.test(img.alt)
);
const screenshotImages = allLocalImages.filter(img => {
  if (options.screenshot) {
    return path.resolve(path.dirname(readmePath), decodeURIComponent(img.dest)) === path.resolve(options.screenshot);
  }
  return /screenshot|screen-shot|截图/i.test(img.dest + " " + img.alt)
    && !/\.svg$/i.test(img.dest);
});

const screenshotPath = screenshotImages[0]
  ? path.resolve(path.dirname(readmePath), decodeURIComponent(screenshotImages[0].dest))
  : null;

const qrPath = qrImages[0]
  ? path.resolve(path.dirname(readmePath), decodeURIComponent(qrImages[0].dest))
  : null;

// Clean text for word / character counting
const withoutCode = markdown.replace(/```[\s\S]*?```/g, " ");
const withoutImages = withoutCode
  .replace(/!\[[^\]]*\]\([^)]*\)/g, " ")
  .replace(/<img\s+[^>]*>/gi, " ");
const withoutDestinations = withoutImages
  .replace(/\[([^\]]+)\]\([^)]*\)/g, "$1")
  .replace(/https?:\/\/\S+/g, " ")
  .replace(/<[^>]+>/g, " ");

const hanCount = (withoutDestinations.match(/\p{Script=Han}/gu) || []).length;
const nonHan = withoutDestinations.replace(/\p{Script=Han}/gu, " ");
const englishWordCount = (nonHan.match(/[\p{L}\p{N}]+(?:['’-][\p{L}\p{N}]+)*/gu) || []).length;

// These are only language signals, not proof of translation completeness.
function prose(text) {
  return text.replace(/```[\s\S]*?```/g, " ")
    .replace(/!\[[^\]]*\]\([^)]*\)/g, " ")
    .replace(/\[[^\]]*\]\([^)]*\)/g, " ")
    .replace(/<a\b[^>]*>[\s\S]*?<\/a>/gi, " ")
    .replace(/https?:\/\/\S+/g, " ")
    .replace(/<[^>]+>/g, " ");
}
const allProse = prose(markdown + "\n" + companion);
const hasBody = text => /\p{Script=Han}{4,}/u.test(prose(text)) || /[A-Za-z]+(?:[ ,]+[A-Za-z]{2,}){2,}/.test(prose(text));
const languageChecks = companionPath ? [
  [linksTo(markdown, readmePath, companionPath), "primary README must link to companion"],
  [linksTo(companion, companionPath, readmePath), "companion README must link to primary"],
] : [];
// Child validation checks images and URLs only; the parent checks both languages.
if (!process.env.HN_README_COMPANION_CHECK) {
  languageChecks.push(
    [/\p{Script=Han}{2,}/u.test(allProse), "Chinese prose is missing"],
    [/[A-Za-z]+(?:[ ,]+[A-Za-z]{2,}){2,}/.test(allProse), "English prose is missing"],
  );
}
const checks = [
  ...languageChecks,
  [hasBody(markdown), "README explanatory prose is missing"],
  [markdown.includes(repoUrl), `repository URL is missing: ${repoUrl}`],
  [markdown.includes(demoUrl), `Demo URL is missing: ${demoUrl}`],
  [Boolean(screenshotPath), "a repository-relative screenshot is missing"],
  [Boolean(screenshotPath && fs.existsSync(screenshotPath)), `screenshot file does not exist: ${screenshotPath || "unknown"}`],
  [Boolean(qrPath), "a repository-relative QR code image (e.g. assets/qr.png) is missing"],
  [Boolean(qrPath && fs.existsSync(qrPath)), `QR code file does not exist: ${qrPath || "unknown"}`],
  [options.preserveLength || hanCount <= maxHan, `Chinese text is ${hanCount} characters; maximum is ${maxHan}`],
  [options.preserveLength || englishWordCount <= maxEnglish, `English text is ${englishWordCount} words; maximum is ${maxEnglish}`],
];

if (additionalUrl) {
  checks.push([
    markdown.includes(additionalUrl),
    `Additional public URL is missing: ${additionalUrl}`,
  ]);
}

const failures = checks.filter(([ok]) => !ok).map(([, message]) => message);
if (failures.length) {
  console.error(`README validation failed for ${readmePath}:`);
  for (const failure of failures) console.error(`- ${failure}`);
  process.exit(1);
}

if (companionPath) {
  const childArgs = [fileURLToPath(import.meta.url), companionPath, repoUrl, demoUrl, String(maxHan), String(maxEnglish)];
  if (additionalUrl) childArgs.push(additionalUrl);
  if (options.screenshot) childArgs.push("--screenshot", path.resolve(options.screenshot));
  if (options.preserveLength) childArgs.push("--preserve-length");
  const result = spawnSync(process.execPath, childArgs, {
    stdio: "inherit", env: { ...process.env, HN_README_COMPANION_CHECK: "1" },
  });
  if (result.status !== 0) process.exit(1);
}
console.log(
  `README validation passed: Chinese ${hanCount}/${maxHan} chars, English ${englishWordCount}/${maxEnglish} words, screenshot/QR files exist and public URL text is present (translation accuracy, online state and QR target are not checked${options.preserveLength ? "; length limits not enforced" : ""}).`
);
