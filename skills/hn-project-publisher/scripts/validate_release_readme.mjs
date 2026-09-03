#!/usr/bin/env node

import fs from "node:fs";
import path from "node:path";
import process from "node:process";

function usage() {
  console.error("Usage: validate_release_readme.mjs <README> <repo-url> <pages-url> [max-han] [max-english] [cloudflare-url]");
  process.exit(2);
}

const [, , readmeArg, repoUrl, pagesUrl, arg4, arg5, arg6] = process.argv;
if (!readmeArg || !repoUrl || !pagesUrl) usage();

let maxHan = 500;
let maxEnglish = 500;
let cloudflareUrl = "";

if (arg4) {
  if (/^https?:\/\//i.test(arg4) || arg4.includes(".xiaosang.cc")) {
    cloudflareUrl = arg4;
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
    cloudflareUrl = arg5;
  } else {
    const num = Number.parseInt(arg5, 10);
    if (Number.isInteger(num) && num > 0) {
      maxEnglish = num;
    }
  }
}

if (arg6) {
  cloudflareUrl = arg6;
}

const readmePath = path.resolve(readmeArg);
if (!fs.existsSync(readmePath)) {
  console.error(`Error: README file not found at ${readmePath}`);
  process.exit(1);
}

const markdown = fs.readFileSync(readmePath, "utf8");

// Extract all image paths (both Markdown and HTML img tags)
const mdImageMatches = [...markdown.matchAll(/!\[([^\]]*)\]\(((?!https?:\/\/)[^)]+)\)/g)];
const htmlImageMatches = [...markdown.matchAll(/<img\s+[^>]*?src=["']((?!https?:\/\/)[^"']+)["'][^>]*>/gi)];

function cleanDest(dest) {
  return dest?.trim().replace(/^<|>$/g, "").split(/[?#]/, 1)[0];
}

const allLocalImages = [
  ...mdImageMatches.map(m => ({ alt: m[1] || "", dest: cleanDest(m[2]) })),
  ...htmlImageMatches.map(m => ({ alt: "", dest: cleanDest(m[1]) })),
];

// Detect screenshot vs QR code
const qrImages = allLocalImages.filter(img =>
  /(qr|qrcode|扫码)/i.test(img.dest) || /(qr|qrcode|扫码)/i.test(img.alt)
);
const screenshotImages = allLocalImages.filter(img =>
  !(/(qr|qrcode|扫码)/i.test(img.dest) || /(qr|qrcode|扫码)/i.test(img.alt))
);

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

const checks = [
  [markdown.includes(repoUrl), `repository URL is missing: ${repoUrl}`],
  [markdown.includes(pagesUrl), `Pages URL is missing: ${pagesUrl}`],
  [Boolean(screenshotPath), "a repository-relative screenshot is missing"],
  [Boolean(screenshotPath && fs.existsSync(screenshotPath)), `screenshot file does not exist: ${screenshotPath || "unknown"}`],
  [Boolean(qrPath), "a repository-relative QR code image (e.g. assets/qr.png) is missing"],
  [Boolean(qrPath && fs.existsSync(qrPath)), `QR code file does not exist: ${qrPath || "unknown"}`],
  [hanCount <= maxHan, `Chinese text is ${hanCount} characters; maximum is ${maxHan}`],
  [englishWordCount <= maxEnglish, `English text is ${englishWordCount} words; maximum is ${maxEnglish}`],
];

if (cloudflareUrl) {
  checks.push([
    markdown.includes(cloudflareUrl),
    `Cloudflare custom domain URL is missing: ${cloudflareUrl}`,
  ]);
}

const failures = checks.filter(([ok]) => !ok).map(([, message]) => message);
if (failures.length) {
  console.error(`README validation failed for ${readmePath}:`);
  for (const failure of failures) console.error(`- ${failure}`);
  process.exit(1);
}

console.log(
  `README validation passed: Chinese ${hanCount}/${maxHan} chars, English ${englishWordCount}/${maxEnglish} words, screenshot, QR code, and public links verified.`
);
