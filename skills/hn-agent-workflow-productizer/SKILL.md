---
name: hn-agent-workflow-productizer
description: Convert fragile manual agent procedures into safe, stateful product workflows. Use when the user wants to productize a prompt-driven process, design an agent sandbox, define deterministic rails, add side-effect verification, create API/Skill boundaries, model workflow state, recover from failures, or decide which parts belong to code versus agent judgment.
---

# HN Agent Workflow Productizer

## Purpose

Turn a manual or prompt-heavy agent workflow into a reliable product design. Preserve the useful intelligence of an agent while moving authority, state, side effects, retries, and verification into deterministic software.

## Core Thesis

The user should express intent. The product should own state and side effects. The agent should reason inside a task-scoped sandbox and return typed decisions or action intents.

## Operating Rules

- Do not port a prompt workflow line by line. Extract the proven effects and invariants.
- Treat chat history as non-durable. Persist workflow truth in a database, filesystem, queue, or explicit artifact.
- Give agents scoped handles and evidence, not raw global credentials, URLs, directory ids, delete authority, or production-wide tools.
- Bind decisions to snapshots. Execute only candidates or records observed in the current task context.
- Verify every side effect by rereading real state from the external system.
- Separate deterministic work, agent judgment, policy validation, execution, and notification.
- Prefer recoverable states over narrative failure.

## Workflow

1. Describe the current manual process.
   - Inputs, trigger, human decisions, tools used, side effects, success criteria, common failures.

2. Extract invariants.
   - Use `references/invariant-map.md`.
   - Preserve effects such as "create target", "choose from observed candidates", "execute", "reread", "mark only after evidence".

3. Split authority.
   - Code owns state, credentials, queues, side effects, retries, policy checks, and audit logs.
   - Agent owns semantic judgment, recovery strategy within bounds, candidate comparison, and uncertainty explanation.

4. Design the sandbox.
   - Expose read-only evidence tools first.
   - Expose side-effect tools only through scoped ids and validated action intents.
   - Convert guard failures into evidence the agent can adapt to.

5. Model workflow state.
   - queued, running, waiting, succeeded, partial, no_coverage/no_match, needs_reconnect, failed, retry_scheduled.
   - Define idempotency, dedupe keys, retry budgets, and orphan recovery.

6. Define verification and audit.
   - For each side effect, define what real state must be reread.
   - Record attempts, selected candidates, rejected candidates, guard refusals, final outcome, and user-facing explanation.

7. Produce the productization plan.
   - API shape, data model, workflow stages, sandbox tools, guardrails, validation tests, and rollout slices.

## Output Shape

```text
Productized workflow:
- User intent:
- Durable state:
- Deterministic steps:
- Agent judgment steps:
- Sandbox tools:
- Side effects and verification:
- Failure states:
- First implementation slice:
- Tests:
```

## References

- Read `references/invariant-map.md` when converting an existing prompt or manual checklist.
- Read `references/sandbox-design.md` when designing agent tools, permissions, guards, and side-effect verification.
