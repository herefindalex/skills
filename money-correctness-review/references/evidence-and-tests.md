# Evidence discipline and verification planning

This file operationalizes the article's distinction between a reported problem, an inspected implementation, and an executed test.

## Evidence is attached to a claim, not to a whole repository

Use these evidence labels independently of severity:

| Label | What it supports | What it does not support |
| --- | --- | --- |
| POLICY | A supplied or documented requirement | That the implementation follows it |
| REPORTED | A public/user report with stated conditions | Independent reproduction or current applicability |
| STATIC | A traced code/constraint/contract argument | An executed workload, unspecified deployment, or production loss |
| LOCAL-TEST | The recorded synthetic test and its result | Unmodeled paths or database/provider behavior |
| DB-TEST | Tested database versions and controlled schedules | Every possible interleaving or all deployments |
| PROVIDER-EVIDENCE | Authorized retained provider observations | A different rail, version, account, or request class |
| PROD-EVIDENCE | Authorized supplied production evidence | Unseen events or a blanket correctness certification |

Do not seek production access merely to obtain a higher label. Use the evidence supplied or explicitly permitted.

## Finding admission checklist

A verified defect needs all of the following:

- An intended contract with an identified authority.
- A target revision and reachable preconditions.
- An inspected path through relevant wrappers and enforcement layers.
- A contradiction supported by complete static evidence or an executed test.
- A bounded impact statement, including whether an external monetary effect was observed.

Static proof can be sufficient for a defect in a pure calculation. A suspected race is not verified merely because two statements are separated in source; inspect the surrounding locks, isolation, constraints, caller behavior, and concurrency assumptions.

Maintain separate fields for classification, evidence level, impact, and priority. An unresolved accounting-policy question can be high consequence without being a verified code defect. Do not invent numerical loss estimates or assert exploitability.

## Primary-source handling

For external issue/PR cases, record system/repository, number, exact title, direct URL, reported version, inspected base/head or merge revision, retrieval date, and current status if actually fetched. Read the patch and the relevant comments/tests, not just the description.

Separate report diagnosis, author claims, maintainer conclusions, inspected code behavior, and your inference. Use “appears to,” “may,” or “likely cause” when the evidence is incomplete. An open proposal is not an accepted fix, and a merged PR is not necessarily in a release.

Bundled article sources are historical research leads. Recheck material provider rules and target versions rather than copying cached statuses or idempotency retention values. When web access is unavailable, use supplied evidence and name what could not be verified.

## Local repository protocol

Begin with the provided revision and read-only inspection. Typical checks, only where tools are available, are `git status --short`, `git rev-parse HEAD`, the task's explicit diff range, symbol search, and reading the relevant code and tests. Do not fetch, switch branches, or compare to an assumed latest baseline without a reason and permission.

Exclude vendored dependencies, generated files, customer dumps, and secrets from broad searches unless they are explicitly necessary and safe. Inspect test setup and environment variable use before running a test. A “test” command may still call a real provider or change a shared database.

Authorized verification should use a disposable directory or worktree and synthetic local dependencies. Record every change and command. Do not execute exploit workflows against third-party systems, autonomously reproduce security vulnerabilities, or perform live financial mutations.

## Verification ladder

**Arithmetic.** Pin units and use exact values. Include ties, zero, maximal valid values, division remainders, and overflow boundaries. Verify formula inputs separately from arithmetic outputs.

**Stateful model.** Generate valid commands and targeted invalid commands. Track business identity, reservations, sources, reversals, expiry, and closure. Compare the system model to a simpler independent oracle when available. Avoid tests that compute expected results using the same defective function.

**Database.** Use coordinated sessions or barriers to force a contested read/commit schedule. Assert committed financial totals, attribution, operation outcomes, and constraint/lock behavior. Explicitly inspect failed transactions and retries; do not simply suppress exceptions.

**Crash windows.** In an authorized local harness, distinguish uncommitted intent, committed work not dispatched, external side effect without recorded acknowledgement, and acknowledged result with publication pending. A fake provider must be able to move its synthetic state before losing the response.

**Delivery.** Duplicate an observation and reorder independent deliveries. Check stable operation correlation, effect deduplication, and allowed state transitions. Reconciliation convergence is conditional on eventually obtaining sufficient authoritative evidence; no algorithm can infer permanently missing facts for free.

**Reconciliation.** Use synthetic batches with equal totals but different member identities, duplicates, fees, late reversals, and unmatched entries. Verify import identity, difference classification, correction links, and exception ownership.

## Test specifications must state equivalence conditions

- Same operation replay means the same relevant fingerprint, not just an equal amount.
- Allocation permutation means the same IDs, eligibility, priority, and policy, not changing FIFO economics.
- Partition invariance means the same fixed refundable units or a declared equivalent amount policy. Different unit selection or crossing expiry can change legitimate outcomes.
- Delivery permutation applies to equivalent observations; causally distinct business actions cannot always be permuted.
- Nonnegative remaining balance is a policy-dependent rule. Authorized credit/overdraft products require their actual credit limit instead.

## Test result vocabulary

Use `proposed`, `not run`, `executed/pass`, `executed/fail`, or `blocked`, with the command/environment and observed output. Keep these separate from `upstream author reports pass` and `test source inspected`.

For a local regression, record baseline failure and patched success only if both executions actually occurred. Otherwise say exactly which side ran. Keep raw output where the task permits; do not write evidence into the target repository without authorization.

## Useful rejection criteria for low-quality findings

Reject or downgrade a finding when it depends only on a code keyword, a missing architecture fashion, an external incident in another system, a test that manually manufactures the expected imbalance, or an unverified assumption about business policy. Preserve the reason in a short rejected-candidates section when useful.

Do not say “use transactions,” “use Decimal,” “add idempotency,” or “add logs” without naming the protected invariant, resource scope, commit/evidence boundary, and a falsifying test.
