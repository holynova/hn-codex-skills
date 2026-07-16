---
name: hn-data-to-github-pages-gallery
description: 将结构化数据和批量图片转换为经过验证的 GitHub Pages 图库或数据网站。用于用户要求发布抓取数据、AI 图片集、食谱合集、清单、作品展示、卡片网格、可搜索表格、批次切换、占位图优先的图库、移动端详情弹窗，或向现有静态网站追加数据和图片。除非交付物是静态导出，否则不要用于依赖实时后端或数据库的应用。
---

# HN Data to GitHub Pages Gallery

## Purpose

Transform raw data, prompt outputs, generated images, or scraped collections into a maintainable GitHub Pages site. The default product is a data-driven static gallery/table with search, filters, compact mobile controls, detail views, and verified live publishing.

## Data Contract

Prefer a single data file that can grow across batches:

```json
{
  "id": "stable-id",
  "title": "Display title",
  "date": "2026-01-01",
  "batch": "initial|2026-01-append",
  "source": "xiaohongshu|manual|github|opencli|...",
  "tags": ["tag"],
  "description": "Short summary",
  "image": "assets/images/item.webp",
  "thumbnail": "assets/thumbs/item.webp",
  "source_url": "https://...",
  "status": "placeholder|generated|verified"
}
```

Keep old data and new data distinguishable with `batch`, `source`, `first_seen`, or `collection` fields. Do not collapse batches if the user asked for table switching.

## Workflow

1. **Orient in the existing site or create a new one.**
   - Inspect repository structure, branch, README, deploy target, existing data files, image directories, and current git status.
   - If creating new, choose a simple static structure: `index.html`, `assets/`, `data.json`, optional `README.md`.
   - Completion criterion: site entry point and data source are identified.

2. **Normalize the dataset.**
   - Convert scraped or generated material into stable JSON/CSV.
   - Assign stable IDs and preserve source URLs.
   - Add batch/source fields for toggles and future appends.
   - Sort defaults by the user's product intent, often newest post date first for social content.
   - Completion criterion: item count, required fields, and duplicate handling are verified.

3. **Design the default UI shell.**
   - Include card grid and/or large table depending on the data.
   - Add compact controls: search, batch/table switcher, tags, sort, and view mode where useful.
   - Keep controls mobile-safe and low vertical overhead.
   - Use detail modals for rich item views and image enlargement.
   - Completion criterion: every control maps to data fields and works without a backend.

4. **Handle images in phases.**
   - Placeholder-first is acceptable when the dataset is ready before images.
   - Put generated/verified images under predictable paths.
   - Convert large image sets to WebP thumbnails and full-size assets.
   - Track missing images with `status` instead of silently broken links.
   - Completion criterion: the page does not show broken image URLs for known items.

5. **Implement deterministically.**
   - Prefer data-driven rendering from JSON embedded or fetched by the page.
   - Avoid hand-duplicating hundreds of cards in HTML.
   - Keep JS small and testable; extract inline scripts for syntax checks if needed.
   - Completion criterion: local static rendering shows the expected item count.

6. **Verify locally.**
   - Run syntax checks (`node --check` for JS, JSON parse for data).
   - Serve with a local static server when interactions matter.
   - Exercise search, filters, batch switcher, sort, modal, and mobile viewport.
   - Completion criterion: core interactions work against the real data.

7. **Publish to GitHub Pages.**
   - Commit only the intended changes.
   - Push to the correct branch.
   - Poll the cache-busted Pages URL until it returns HTTP 200 and contains expected markers.
   - Completion criterion: live URL shows the expected item count or known marker.

8. **Report product state.**
   - Include live URL, repo path, item count, image count, placeholders remaining, commit hash, and verification.
   - If images are not complete, state the next batch boundary clearly.

## Common Pitfalls

1. **Mixing old and new batches without labels.** Add `batch` or `collection` so the UI can switch views.
2. **Hardcoding cards.** Use JSON data rendering; future appends should not require manual HTML surgery.
3. **Letting mobile controls sprawl.** Compact filters and sticky controls should not eat the whole phone screen.
4. **Publishing before live verification.** GitHub Pages can lag; verify with a cache-busting query.
5. **Broken image optimism.** If images are pending, mark placeholders explicitly and avoid broken URLs.

## References

- Read `references/static-gallery-checklist.md` before local and live verification.
