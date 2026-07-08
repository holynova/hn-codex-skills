# Report State Schema

Recommended daily file:

```json
{
  "date": "2026-01-01",
  "fetched_at": "2026-01-01T18:00:00+08:00",
  "source": "source-name-or-url",
  "items": []
}
```

Recommended history file:

```json
{
  "last_updated": "2026-01-01",
  "items": {
    "stable-id": {
      "first_seen": "2026-01-01",
      "last_seen": "2026-01-01",
      "title": "...",
      "url": "..."
    }
  },
  "dates": {
    "2026-01-01": {
      "total_items": 0,
      "total_new": 0,
      "total_changed": 0
    }
  }
}
```

Use source-specific field names if the existing project already has a schema, but keep item identity and dates explicit.
