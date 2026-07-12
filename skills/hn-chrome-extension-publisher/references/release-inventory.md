# Release Inventory

Inspect existing files before producing anything new.

## Project

- Source and built `manifest.json`
- Build, test, lint, and type-check commands
- Extension UI entry points and primary user flow
- Existing extension ID, Chrome Web Store item URL/ID, publisher, and visibility
- Current local and last published versions
- Permissions, host permissions, content scripts, service worker, remote requests, storage, analytics, auth, payments, and ads
- Existing license, support contact, website, privacy policy, release notes, and prior ZIP/CRX packages

## Product Quality

- Load the production build through `chrome://extensions` in Developer Mode.
- Verify install/reload, popup/action, options/side panel, content-script behavior, service-worker lifecycle, keyboard commands, onboarding, and error states that exist.
- Inspect the extension service worker and relevant page consoles for errors.
- Test only declared supported environments and avoid claiming untested compatibility.

## Policy Review

- State one narrow, understandable purpose.
- Map every permission and host pattern to a user-facing feature.
- Prefer `activeTab`, optional permissions, and narrow host patterns when they meet the feature need.
- Inspect bundled JavaScript for remote executable code, `eval`, dynamic script injection, hidden behavior, and development endpoints.
- Document every category of user data handled, including data processed or stored only on the device.
- Ensure store descriptions, screenshots, privacy policy, dashboard disclosures, and actual behavior agree.

## Deliverables

- Uploadable extension ZIP
- Store listing copy and release notes
- Store icon, screenshots, and small promo image
- Optional marquee image and demo video URL
- Privacy practices answers and permission justifications
- Stable privacy-policy URL and support contact/URL
- Audit report including warnings and unresolved decisions
