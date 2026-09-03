# Batch Artifacts

Every completed batch should be self-contained:

- `README.md`: goal, backend, prompt source, counts, known failures, verification.
- `prompts.txt`: human-readable numbered prompts.
- `prompts.json`: complete structured prompt data.
- `prompts.jsonl`: one item per line for scripts and resume runs.
- `images/`: raw accepted project copies.
- `renamed/`: stable delivery filenames.
- `mapping.csv`: ID, title, backend, prompt, source path, final path, dimensions, status.
- `contact_sheet.jpg`: quick visual audit.
- `batch.log`: chronological generation and validation log.
- `<project>.zip`: all deliverable assets.

Keep the project under a user-selected output root. When comparing backends, preserve separate paths instead of overwriting:

```text
chatgpt_images/
gemini_images/
renamed_chatgpt/
renamed_gemini/
mapping_chatgpt.csv
mapping_gemini.csv
contact_sheet_chatgpt.jpg
contact_sheet_gemini.jpg
```
