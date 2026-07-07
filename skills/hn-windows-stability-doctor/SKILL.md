---
name: hn-windows-stability-doctor
description: Diagnose Windows stability problems and produce evidence-based repair plans. Use when the user reports blue screens, unexpected restarts, freezes, dump files, WHEA/NVMe resets, memory corruption, driver crashes, download-related crashes, BIOS/EXPO/PBO/Curve Optimizer concerns, disk-health suspicion, startup/app conflicts, or asks to verify whether a prior repair fixed a Windows crash problem.
---

# HN Windows Stability Doctor

## Purpose

Diagnose Windows instability from evidence before recommending fixes. Treat crashes as a system investigation: collect timestamps, correlate events, identify the most likely failing layer, apply the least risky repair first, and verify after reboot or workload replay.

## Operating Rules

- Start with a timeline: exact crash times, user-visible symptom, recent software/hardware changes, and whether the crash happened during download, gaming, model loading, idle, boot, or shutdown.
- Prefer built-in read-only evidence first: Event Viewer logs, Reliability Monitor data, dump metadata, driver versions, disk SMART/NVMe health, memory test results, and Windows update history.
- Avoid destructive fixes until evidence supports them. Do not recommend BIOS flashing, registry edits, driver removal, overclock changes, or disk operations casually.
- Never treat one signal as proof. Correlate at least two sources when possible, such as dump bugcheck + System log + hardware sensor/SMART.
- If dump analysis can freeze the machine, copy dumps to a working folder and inspect metadata first. Analyze one dump at a time.
- Separate "likely root cause", "possible contributor", and "not supported by evidence".
- Finish with a verification checklist the user can run after the fix.
- For repeated Codex environment friction, use the preflight checklist before deeper diagnosis.

## Workflow

1. Scope the incident.
   - Ask only for missing essentials: crash time, symptom, recent changes, and whether a dump exists.
   - If the user asked for direct action on the current machine, gather evidence with commands instead of giving abstract advice.

2. Build the evidence table.
   - Use `references/evidence-checklist.md` for the command/source checklist.
   - Include date/time, source, event or bugcheck, involved device/driver, confidence, and note.

3. Classify the failure layer.
   - OS/driver: bugcheck names, display/network/storage driver failures, repeated service crashes.
   - Storage: NVMe resets, disk warnings, controller errors, download/write-load correlation.
   - Memory/CPU stability: memory corruption, WHEA, random modules, EXPO/PBO/Curve Optimizer enabled, stress/load correlation.
   - App/runtime: specific app install, anti-cheat, downloader, model runtime, GPU runtime, extension/service conflict.

4. Recommend the smallest repair set.
   - For each fix, explain why it matches evidence, risk level, rollback path, and verification method.
   - Defer high-risk firmware/BIOS steps unless the evidence points there or lower-risk repairs failed.

5. Verify.
   - Re-check Event Viewer/Reliability Monitor after reboot.
   - Re-run the triggering workload when safe.
   - Compare crash frequency and new event signatures against the original evidence.

## Output Shape

Use this structure for diagnostic answers:

```text
Summary:
- Most likely cause:
- Confidence:
- Why:

Evidence:
| Time | Source | Signal | Meaning | Confidence |

Recommended actions:
1. ...

Verification:
- ...

Residual risk:
- ...
```

## References

- Read `references/evidence-checklist.md` for Windows evidence sources and safe command patterns.
- Read `references/repair-playbook.md` before proposing driver, disk, memory, BIOS, or overclock changes.
- Read `references/codex-preflight.md` when the task involves Codex, PowerShell, npm/npx shims, encoding, Git/GitHub CLI, Node, Python, Docker, or recurring local development setup problems.
- Use `scripts/codex_preflight.ps1` for a safe, read-only Windows/Codex environment check.
