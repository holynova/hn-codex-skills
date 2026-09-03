# Invariant Map

Use this file to convert a prompt-heavy or manual agent process into product invariants.

## Extract Effects

For each manual step, record:

- Input evidence.
- Decision made by human or agent.
- Side effect performed.
- External system touched.
- Verification method.
- Failure or retry behavior.

Then rewrite each as an invariant:

- "Only execute candidates selected from the current snapshot."
- "Only mark complete after rereading the target state."
- "Only delete files that were listed in a scoped task directory."
- "Never use hidden chat memory as durable state."

## Split The Process

Use these buckets:

- Deterministic code: parsing, persistence, queueing, retries, idempotency, policy checks, API calls, credential handling.
- Agent judgment: semantic matching, ambiguous selection, recovery strategy, explanation, uncertainty.
- Human decision: legal/business policy, irreversible destructive action, credential provision, low-confidence cases if unattended operation is not acceptable.

## Minimum Product Model

For each workflow, define:

- Intent: what the user asked for.
- Scope: account, project, directory, record set, environment.
- State: queued, running, waiting, succeeded, partial, no_match, failed, needs_attention.
- Snapshot: external evidence captured before selection.
- Decision: structured output bound to snapshot ids.
- Attempt: each side-effect execution.
- Verification: external reread after each side effect.
- Notification or result: user-facing summary.

## Migration Warning

Do not preserve method names or prompt steps just because they exist. Preserve the effect and safety property.
