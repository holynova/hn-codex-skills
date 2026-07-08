---
name: hn-stateful-cron-report-pipeline
description: Build and maintain stateful recurring reports and watchdogs. Use when the user asks for a daily or weekly cron report, source monitoring, yesterday comparison, compact Chinese digest, GitHub Trending/flysheep-style updates, local history JSON, strict Telegram output formats, failure summaries, first-run tests, or cron jobs that must save state before pushing results.
---

# HN Stateful Cron Report Pipeline

## Purpose

Create recurring report jobs that are durable, stateful, verifiable, and concise. This skill is for cron reports that fetch live data, compare against prior runs, save local history, and send a user-shaped digest without hallucinated results.

## When to Use

- The user asks for a daily/weekly report, monitor, digest, alert, or scheduled scrape.
- The report needs to compare today with yesterday or detect newly seen items.
- The output must follow a strict compact format, especially Chinese Telegram summaries.
- The task needs local JSON history under `~/.hermes/` or project state files.
- The job wraps a CLI/script such as `pnpm daily`, `game-tier`, `nlm`, or a browser-only scrape.
- The user asks to modify an existing cron job and run it once for verification.

Don't use for one-shot research with no recurring state.

## State Model

Every stateful report needs explicit files:

```text
~/.hermes/<report-name>/
  YYYY-MM-DD.json
  history.json
  last-run.json
  logs/
```

For project-local jobs, keep state under the project if that is already the source of truth, and document the path in the cron prompt.

Minimum per-item fields:

```json
{
  "id": "stable-id-or-url",
  "title": "Display title",
  "url": "https://...",
  "first_seen": "2026-01-01",
  "last_seen": "2026-01-02",
  "metadata": {},
  "status": "new|seen|changed|failed"
}
```

## Workflow

1. **Define the report contract.**
   - Identify source, schedule, destination, state path, item identity, comparison rule, and exact output format.
   - If the user has a preferred format, preserve it literally and remove extra sections.
   - Completion criterion: the cron prompt can run in a fresh session without chat context.

2. **Choose the right fetch path.**
   - Prefer dedicated CLI commands when available.
   - Use API or terminal fetches for stable endpoints.
   - Use browser extraction when the host blocks terminal/API access or the page requires browser context.
   - Document source-specific quirks in the prompt or script.
   - Completion criterion: one real fetch returns parseable current data.

3. **Persist before reporting.**
   - Save the full current dataset for the run date.
   - Update history/index files atomically.
   - Keep raw data separate from formatted report text.
   - Completion criterion: a failed delivery does not lose fetched state.

4. **Compare deterministically.**
   - Identify `new`, `changed`, `missing`, and `unchanged` from stable IDs.
   - On first run, follow the chosen first-run behavior: mark all as new or send a setup report.
   - Completion criterion: comparison can be re-run from files and produce the same result.

5. **Format tightly.**
   - Match the requested output exactly.
   - For compact Chinese digests, include only the requested sections and short human explanations.
   - Suppress English raw descriptions when the user asked for Chinese-only summaries.
   - Completion criterion: no extra “summary”, “done”, debug logs, or unrelated sections appear.

6. **Handle failures as report data.**
   - If a wrapped command partially succeeds, parse the current run log for success/failure items.
   - Include concise failure reasons only when the requested format allows them.
   - Never fabricate missing source data; say the fetch failed or send `[SILENT]` only when the job contract allows silence.
   - Completion criterion: failure output is grounded in command output or logs.

7. **Create or update the cron job.**
   - Make the prompt self-contained.
   - Attach skills only if they are available to future runs.
   - Use `enabled_toolsets` to minimize tool load when obvious.
   - Use a script/no-agent job when the script itself produces the exact desired message.
   - Completion criterion: `cronjob(action='run')` or an immediate equivalent test completes once.

8. **Verify the first run.**
   - Confirm state files exist.
   - Confirm output format matches the contract.
   - Confirm item counts are from the current run only when requested.
   - Completion criterion: the user can trust the next scheduled run without manual cleanup.

## Common Pitfalls

1. **Cron prompt depends on chat history.** Future cron sessions start fresh; include paths, schema, format, and source quirks.
2. **Reporting before saving state.** Save data first, then send the digest.
3. **Parsing cumulative logs as current run.** Use run timestamps or generated log paths to count only this run.
4. **Using terminal for browser-only sources.** If a site blocks curl/API, encode the browser extraction method in the job.
5. **Noisy reports.** User-facing cron output should be compact; debug details belong in logs.
6. **Recursive cron creation.** Cron-run sessions should not schedule more cron jobs unless explicitly designed outside the run.

## Verification Checklist

- [ ] Source fetch was tested with real output.
- [ ] State directory and JSON files are created/updated.
- [ ] Comparison uses stable IDs and handles first run.
- [ ] Output exactly matches the requested format.
- [ ] Existing cron job was updated or new job created with self-contained prompt.
- [ ] A one-shot run/test completed, or the blocker is reported honestly.
