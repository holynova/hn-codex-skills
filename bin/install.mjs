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
  "hn-tool-ui-polisher",
  "hn-visual-asset-pipeline",
  "hn-opencli-batch-image-production",
  "hn-data-to-github-pages-gallery",
  "hn-stateful-cron-report-pipeline",
  "hn-xiaohei-draw",
  "hn-project-publisher",
  "hn-chrome-extension-publisher",
  "hn-ui-layout-typography-audit",
  "hospital-record-collector",
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

function createInstallPlan(names, skillsDir, options) {
  return names.map((name) => {
    const source = path.join(sourceSkillsDir, name);
    const target = path.join(skillsDir, name);
    assertSafeTarget(skillsDir, target);

    if (!fs.existsSync(source) || !fs.statSync(source).isDirectory()) {
      throw new Error(`Missing bundled skill at ${source}`);
    }
    if (!fs.existsSync(path.join(source, "SKILL.md"))) {
      throw new Error(`Bundled skill is missing SKILL.md: ${source}`);
    }
    if (!fs.existsSync(path.join(source, "agents", "openai.yaml"))) {
      throw new Error(`Bundled skill is missing agents/openai.yaml: ${source}`);
    }
    if (fs.existsSync(target) && !options.force) {
      throw new Error(`Target already exists: ${target}. Re-run with --force to replace it.`);
    }
    return { name, source, target, staging: null, backup: null };
  });
}

function removeIfExists(target) {
  if (target && fs.existsSync(target)) {
    fs.rmSync(target, { recursive: true, force: true });
  }
}

function stageInstallPlan(plan, skillsDir) {
  fs.mkdirSync(skillsDir, { recursive: true });
  const token = `${process.pid}-${Date.now()}-${Math.random().toString(16).slice(2)}`;
  try {
    for (const item of plan) {
      item.staging = path.join(skillsDir, `.${item.name}.install-${token}`);
      item.backup = path.join(skillsDir, `.${item.name}.backup-${token}`);
      removeIfExists(item.staging);
      removeIfExists(item.backup);
      fs.cpSync(item.source, item.staging, { recursive: true, errorOnExist: true, force: false });
      if (!fs.existsSync(path.join(item.staging, "SKILL.md"))) {
        throw new Error(`Staged skill is incomplete: ${item.name}`);
      }
    }
  } catch (error) {
    for (const item of plan) removeIfExists(item.staging);
    throw error;
  }
}

function applyInstallPlan(plan) {
  const applied = [];
  try {
    for (const item of plan) {
      if (fs.existsSync(item.target)) {
        fs.renameSync(item.target, item.backup);
      } else {
        item.backup = null;
      }
      try {
        fs.renameSync(item.staging, item.target);
      } catch (error) {
        if (item.backup && fs.existsSync(item.backup)) {
          fs.renameSync(item.backup, item.target);
        }
        throw error;
      }
      applied.push(item);
    }
  } catch (error) {
    for (const item of [...applied].reverse()) {
      removeIfExists(item.target);
      if (item.backup && fs.existsSync(item.backup)) {
        fs.renameSync(item.backup, item.target);
      }
    }
    for (const item of plan) removeIfExists(item.staging);
    throw new Error(`Installation failed and was rolled back: ${error.message}`);
  }

  for (const item of applied) {
    if (item.backup && fs.existsSync(item.backup)) {
      try {
        fs.rmSync(item.backup, { recursive: true, force: true });
      } catch (error) {
        console.warn(`Installed ${item.name}, but could not remove backup ${item.backup}: ${error.message}`);
      }
    }
    console.log(`Installed ${item.name}.`);
  }
}

function main() {
  const args = parseArgs(process.argv.slice(2));
  const skillsDir = args.skillsDir || defaultSkillsDir();
  const selected = args.selectedSkill ? [args.selectedSkill] : skillNames;
  const plan = createInstallPlan(selected, skillsDir, args);

  for (const item of plan) {
    console.log(`Source: ${item.source}`);
    console.log(`Target: ${item.target}`);
  }

  if (args.dryRun) {
    console.log("Dry run complete. No files copied.");
    return;
  }

  stageInstallPlan(plan, skillsDir);
  applyInstallPlan(plan);
}

try {
  main();
} catch (error) {
  console.error(`Error: ${error.message}`);
  process.exit(1);
}
