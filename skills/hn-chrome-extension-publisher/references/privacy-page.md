# Privacy Page

Write the policy from the verified data-flow inventory. This is a release artifact, not legal advice.

## Required Content

- Extension and developer identity
- Effective or last-updated date
- What data the extension accesses, collects, stores, or transmits
- Purpose and legal/user-facing reason for each use
- Local storage and sync behavior
- External services and recipients
- Retention and deletion behavior
- Security and transport practices
- User controls, access, and deletion contact
- Limited Use statement when relevant
- Contact/support route
- How policy changes are communicated

If the extension handles no user data, state that accurately while still explaining permissions and local processing. Local-only handling must still match the dashboard disclosures.

## GitHub Pages

Prefer a stable path such as `https://OWNER.github.io/REPO/privacy/`.

1. Add an accessible static page under the site's published root, such as `docs/privacy/index.html` when Pages publishes `master:/docs`.
2. Use the extension name in the page title and visible heading.
3. Avoid analytics, cookies, remote fonts, or trackers on the privacy page unless they are disclosed and necessary.
4. Commit and publish through the repository's existing Pages workflow.
5. Open the public HTTPS URL and verify it without authentication on desktop and mobile.
6. Put the exact canonical URL in `listing.md`, `privacy.md`, and the Developer Dashboard.

When no suitable public repository exists, prepare the page and ask before creating or publishing a new GitHub repository. Do not claim a privacy URL is ready until it is publicly reachable.

Before submission, compare the policy and prepared answers against the current official [Privacy practices fields](https://developer.chrome.com/docs/webstore/cws-dashboard-privacy) and [User Data FAQ](https://developer.chrome.com/docs/webstore/program-policies/user-data-faq/).
