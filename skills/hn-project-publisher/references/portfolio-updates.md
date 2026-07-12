# Portfolio Updates

Update only targets the user explicitly names or project instructions explicitly register.

## Canonical Entry

Prepare one canonical payload before editing any portfolio:

- bilingual or target-language project title
- concise description
- GitHub repository URL
- GitHub Pages URL
- screenshot or thumbnail path/URL
- relevant tags, only when the target supports them

Keep facts and links consistent across targets.

## GitHub Profile

The profile README repository is the public `OWNER/OWNER` repository with a non-empty root `README.md`.

1. Inspect the current README and determine its existing project-list structure.
2. Update an existing entry by repository URL; otherwise add one entry using the current table, cards, or list style.
3. Preserve unrelated content, ordering conventions, badges, and formatting.
4. Commit and push the profile repository only when the publish request authorizes the GitHub profile update.
5. Open `https://github.com/OWNER` and verify the entry and links.

If no profile repository exists, create it only when the user explicitly requested a GitHub homepage/profile update. Make it public and keep any new profile README minimal.

## Other Portfolio Sites

For each named target:

1. Identify the update mechanism in this order: local source repository, official API/connector, documented CLI, authenticated browser.
2. Inspect the existing project schema and visual style before editing.
3. Add or update by canonical repository URL to avoid duplicates.
4. Preserve unrelated content and avoid broad rewrites.
5. Publish through the site's normal workflow only when the user's publish request covers that named target.
6. Open the public portfolio URL and verify title, description, screenshot, repository link, and live-demo link.

Never request that the user paste secrets into chat or save credentials in project files. If authentication, target URL, or edit access is missing, finish all other targets and report that one as blocked with the exact requirement.
