# Sandbox Design

Use this file to design agent tools and authority boundaries.

## Tool Categories

Read-only evidence tools:

- Search scoped sources.
- Inspect current target state.
- Read task snapshots.
- Read prior attempts.

Decision tools:

- Select candidate ids.
- Map files to records.
- Explain no coverage.
- Request a retry strategy.

Side-effect tools:

- Execute a snapshot-bound candidate.
- Move scoped items.
- Delete verified scoped items.
- Mark obtained/complete.
- Finish the workflow.

## Guard Rules

Every side-effect tool should validate:

- The task scope matches the current user/account/project.
- The ids were observed in this task.
- The target is not a protected root or unrelated directory.
- The action is not redundant after coverage is met.
- The operation stays within budget.

Guard failures should return structured evidence where possible:

```json
{ "error": "SAFETY_VIOLATION: candidate was not observed in this task" }
```

The agent can adapt to evidence; the system must still refuse unsafe authority.

## Verification Rules

After each side effect:

- Reread the external system.
- Return the actual new state to the agent or workflow.
- Persist attempts and observed results.
- Derive final status from verified state, not from the agent's narrative.

## Anti-Patterns

- Giving the agent raw production credentials.
- Letting the agent choose arbitrary paths, ids, URLs, or SQL.
- Treating provider/API acceptance as success without rereading.
- Using parser output as the only evidence boundary.
- Leaving failure as prose instead of a recoverable state.
