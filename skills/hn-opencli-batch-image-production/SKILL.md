---
name: hn-opencli-batch-image-production
description: 使用 OpenCLI 可靠地批量生产图片。用于用户要求通过 ChatGPT 或 Gemini 生成大量 AI 图片、在不同后端复用同一组提示词、处理配额或 EMPTY_RESULT 失败、验证图片文件、重试缺失项目、生成重命名副本、映射 CSV、联系表、ZIP 包、批处理日志，或替换网站与图库图片。不要用于无需批量产物的一次性手写生图提示词。
---

# HN OpenCLI Batch Image Production

## Purpose

Turn a batch of prompts into a verified, reusable image package. This skill is for long-running OpenCLI image jobs where reliability matters more than speed: fixed prompt sets, backend parity, retries, quality gates, resumability, renamed outputs, mapping tables, contact sheets, and optional website replacement.

## Project Layout

Read `references/batch-artifacts.md` before creating or changing the batch layout. Keep backend outputs separate instead of overwriting them.

## Workflow

1. **Freeze the prompt set.**
   - Write `prompts.txt`, `prompts.json`, and `prompts.jsonl` before generating.
   - Include stable IDs, display titles, prompt text, intended backend, and expected filename stem.
   - Completion criterion: every planned item has an ID and prompt in all required prompt files.

2. **Interrogate OpenCLI before running.**
   - Run the relevant help command instead of trusting memory: `opencli chatgpt image --help`, `opencli gemini image --help`, and structured help when available.
   - Prefer structured output (`-f yaml` or JSON when available).
   - Completion criterion: the command shape is verified against the installed OpenCLI version.

3. **Use backend-specific command shapes.**
   - ChatGPT image baseline:
     ```bash
     opencli chatgpt image "<prompt>" \
       --window background \
       --site-session persistent \
       -f yaml \
       --op <output_dir> \
       --timeout 240
     ```
   - `--site-session` must be one of `ephemeral` or `persistent`; do not invent custom session names.
   - Gemini can save to `~/AI_outputs/gemini/images/` even when `--op` points elsewhere. After each Gemini generation, locate the newest `gemini_*.png` there and copy it into the project folder.
   - Completion criterion: the first item is generated and its real output path is known.

4. **Run with resume state.**
   - Log each item as `pending`, `success`, `retry`, `failed`, or `blocked`.
   - Keep source output paths, final copied paths, dimensions, file size, backend, and error text.
   - Do not restart completed items unless the user explicitly asks for replacement.
   - Completion criterion: interrupted runs can resume without duplicating completed images.

5. **Apply image quality gates.**
   - For each candidate file, verify it exists and is a real image.
   - Reject tiny placeholders, especially `480x480` or very small files when a full image is expected.
   - Reject all-black, all-transparent, corrupt, or zero-byte images.
   - Use image dimensions and pixel sampling, not just file extension.
   - Completion criterion: every accepted item has dimensions, size, and quality status recorded.

6. **Retry deliberately.**
   - Retry transient failures with bounded attempts.
   - Treat ChatGPT `EMPTY_RESULT`, exit code `66`, and browser timeout as retryable unless quota is visibly hit.
   - If quota/frequency limit is hit, stop, record missing IDs, and prepare a resume command or scheduled retry only if the user asks.
   - For repeated content-filter failures, simplify the prompt while preserving the core concept, style, subject, and labeling requirements.
   - Completion criterion: remaining failures are classified as retryable, quota-blocked, filtered, or hard failed.

7. **Normalize outputs.**
   - Copy accepted images into `renamed/` using stable names such as `001_title_backend.png`.
   - Generate `mapping.csv` with at least: `id,title,backend,prompt,source_path,final_path,width,height,status,error`.
   - Generate a contact sheet with visible ID/title labels.
   - Create a zip containing prompts, README, mapping, contact sheet, logs, and renamed images.
   - Completion criterion: the package can be inspected without reading chat history.

8. **Update website/gallery only after a full audit.**
   - Do not replace live site images until the target set is complete or the user approves partial replacement.
   - Convert to WebP thumbnails/large images when the site uses WebP.
   - Update data references deterministically; preserve IDs and old/new mapping.
   - Completion criterion: local files and site references agree item-for-item.

9. **Report with evidence.**
   - Report counts, missing IDs, paths, zip path, and verification performed.
   - Include blockers honestly; do not claim images exist unless files were verified.

## Common Pitfalls

1. **Trusting stale OpenCLI arguments.** Always check help; OpenCLI session flags and output behavior change.
2. **Believing `--op` for Gemini.** Gemini may save under `~/AI_outputs/gemini/images/`; locate and copy the latest real file.
3. **Counting OpenCLI success as image success.** The CLI can return success while no valid image is present. Validate the file.
4. **Overwriting backend comparisons.** Keep ChatGPT and Gemini outputs in separate folders until the user picks the winner.
5. **Replacing a live gallery before full coverage.** Audit completeness first, then update the site.
6. **Losing provenance.** Keep prompt, backend, source path, final path, and failure reason in mapping CSV.

## Verification Checklist

- [ ] Prompt files exist and item counts match.
- [ ] OpenCLI command shape was checked against installed help.
- [ ] Every accepted image exists, opens, has expected dimensions, and is not black/transparent/tiny.
- [ ] Failures are logged with IDs and reasons.
- [ ] `renamed/`, `mapping.csv`, contact sheet, README, and zip are created.
- [ ] If a website was updated, all referenced files exist and the live/cache-busted URL was verified.

## References

- Read `references/batch-artifacts.md` for the canonical project layout and backend-specific artifact names.
