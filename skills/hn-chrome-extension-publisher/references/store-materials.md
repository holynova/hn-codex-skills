# Store Materials

Use this suggested release structure:

```text
release/chrome-web-store/
├── listing.md
├── privacy.md
├── assets/
│   ├── store-icon-128.png
│   ├── screenshot-01.png
│   ├── screenshot-02.png
│   ├── promo-small-440x280.png
│   └── promo-marquee-1400x560.png  # optional
├── privacy-policy/
│   └── index.html
└── packages/
    └── extension-VERSION.zip
```

## `listing.md`

Use these headings so the release audit can verify completeness:

```markdown
# Store Listing

## Name
## Short Description
## Detailed Description
## Single Purpose
## Category
## Language
## Website
## Support
## Privacy Policy
## Release Notes
```

Fill every applicable section with reviewed content. Include:

- extension name
- manifest short description, at most 132 characters
- detailed store description based on verified features
- single-purpose statement
- primary category and language
- website, support, and privacy-policy URLs
- one concise release-note section for the submitted version
- optional localization sections only when translations are reviewed

Avoid keyword stuffing, unverifiable superlatives, competitor impersonation, fake badges, and functionality not present in the packaged build.

## `privacy.md`

Use these headings:

```markdown
# Privacy Practices

## Single Purpose
## Permission Justifications
## Host Permission Justifications
## Remote Code
## User Data
## Data Transfers and Prohibited Uses
## Limited Use
## Privacy Policy
```

Mark a field `Not applicable` with a short reason when that is the accurate answer; do not delete it. Prepare canonical dashboard answers:

- single purpose
- one justification per permission and host permission
- remote-code declaration and explanation
- user-data categories collected or handled
- whether data is sold, transferred, used for lending/credit, or used beyond the single purpose
- Limited Use certification basis
- privacy-policy URL

Do not select certifications on the user's behalf when the code and data flow do not establish the answer.

## Images

- Store icon: PNG, exactly 128x128. Keep the mark simple and readable on light and dark backgrounds.
- Manifest icons: provide PNG at 16x16, 32x32, 48x48, and 128x128 when applicable, and ensure every manifest path exists.
- Screenshots: 1 to 5 current product screenshots, each exactly 1280x800 or 640x400, square corners, full bleed, and not blurry or text-heavy.
- Small promo image: PNG or JPEG, exactly 440x280; treat it as a branded promotional composition rather than a raw screenshot.
- Marquee image: optional PNG or JPEG, exactly 1400x560.

Inspect key images visually after checking dimensions. Ensure screenshots show the submitted version's real experience and contain no private account data, tokens, unrelated browser tabs, or misleading mock UI.

Before a live submission, refresh requirements from the official [Prepare your extension](https://developer.chrome.com/docs/webstore/prepare), [listing guidance](https://developer.chrome.com/docs/webstore/best-listing), and [image requirements](https://developer.chrome.com/docs/webstore/images) pages because dashboard requirements can change.
