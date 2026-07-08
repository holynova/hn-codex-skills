#!/usr/bin/env node
import fs from "node:fs";
import os from "node:os";
import path from "node:path";
import process from "node:process";
import { fileURLToPath } from "node:url";

const __dirname = path.dirname(fileURLToPath(import.meta.url));
const repoRoot = path.resolve(__dirname, "..");
const sourceSkillsDir = path.join(repoRoot, "skills");
const skillNames = [
  "hn-windows-stability-doctor",
  "hn-frontend-project-shipper",
  "hn-agent-workflow-productizer",
  "hn-product-release-packager",
  "hn-tool-ui-polisher",
  "hn-visual-asset-pipeline",
  "hn-opencli-batch-image-production",
  "hn-data-to-github-pages-gallery",
  "hn-stateful-cron-report-pipeline",
  "hn-xiaohei-draw",
];

function usage(exitCode = 0) {
  console.log(`Usage:
  hn-codex-skills install [skill-name] [--path <skills-dir>] [--force] [--dry-run]
  hn-codex-skills --dry-run

Examples:
  npx github:holynova/hn-codex-skills install
  npx github:holynova/hn-codex-skills install hn-frontend-project-shipper
  npx github:holynova/hn-codex-skills install --force

Options:
  skill-name            Install only one skill. Defaults to all bundled skills.
  --path <skills-dir>   Install into a specific Codex skills directory.
  --force               Replace existing target skill directories.
  --dry-run             Print the planned install location without copying.

Default install path:
  $CODEX_HOME/skills when CODEX_HOME is set, otherwise ~/.codex/skills

Bundled skills:
  ${skillNames.join("\n  ")}
`);
  process.exit(exitCode);
}

function parseArgs(argv) {
  const args = {
    command: "install",
    dryRun: false,
    force: false,
    skillsDir: null,
    selectedSkill: null,
  };

  const rest = [...argv];
  if (rest[0] === "install") {
    rest.shift();
  } else if (rest[0] === "help" || rest[0] === "--help" || rest[0] === "-h") {
    usage(0);
  } else if (rest[0] && !rest[0].startsWith("-")) {
    console.error(`Unknown command: ${rest[0]}`);
    usage(1);
  }

  while (rest.length) {
    const arg = rest.shift();
    if (arg === "--dry-run") {
      args.dryRun = true;
    } else if (arg === "--force") {
      args.force = true;
    } else if (arg === "--path") {
      const value = rest.shift();
      if (!value) {
        throw new Error("--path requires a directory");
      }
      args.skillsDir = path.resolve(value);
    } else if (arg?.startsWith("-")) {
      throw new Error(`Unknown option: ${arg}`);
    } else if (!args.selectedSkill) {
      args.selectedSkill = arg;
    } else {
      throw new Error(`Only one skill name can be specified. Unexpected: ${arg}`);
    }
  }

  if (args.selectedSkill && !skillNames.includes(args.selectedSkill)) {
    throw new Error(`Unknown skill: ${args.selectedSkill}. Expected one of: ${skillNames.join(", ")}`);
  }

  return args;
}

function defaultSkillsDir() {
  if (process.env.CODEX_HOME) {
    return path.join(process.env.CODEX_HOME, "skills");
  }
  return path.join(os.homedir(), ".codex", "skills");
}

function assertSafeTarget(skillsDir, target) {
  const resolvedSkills = path.resolve(skillsDir);
  const resolvedTarget = path.resolve(target);
  const relative = path.relative(resolvedSkills, resolvedTarget);
  if (relative.startsWith("..") || path.isAbsolute(relative)) {
    throw new Error(`Refusing to install outside skills directory: ${resolvedTarget}`);
  }
}

function installSkill(name, skillsDir, options) {
  const source = path.join(sourceSkillsDir, name);
  const target = path.join(skillsDir, name);

  if (!fs.existsSync(source)) {
    throw new Error(`Missing bundled skill at ${source}`);
  }
  assertSafeTarget(skillsDir, target);

  console.log(`Source: ${source}`);
  console.log(`Target: ${target}`);

  if (options.dryRun) {
    return;
  }

  if (fs.existsSync(target) && !options.force) {
    throw new Error(`Target already exists: ${target}. Re-run with --force to replace it.`);
  }

  fs.mkdirSync(skillsDir, { recursive: true });
  if (fs.existsSync(target)) {
    fs.rmSync(target, { recursive: true, force: true });
  }
  fs.cpSync(source, target, { recursive: true });
  console.log(`Installed ${name}.`);
}

function main() {
  const args = parseArgs(process.argv.slice(2));
  const skillsDir = args.skillsDir || defaultSkillsDir();
  const selected = args.selectedSkill ? [args.selectedSkill] : skillNames;

  for (const name of selected) {
    installSkill(name, skillsDir, args);
  }

  if (args.dryRun) {
    console.log("Dry run complete. No files copied.");
  }
}

try {
  main();
} catch (error) {
  console.error(`Error: ${error.message}`);
  process.exit(1);
}
