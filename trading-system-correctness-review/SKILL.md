---
name: trading-system-correctness-review
description: Review trading, execution, market-data, payment, or financially critical transaction systems for production correctness risks that architecture diagrams and ordinary code reviews often miss. Use when reviewing numeric precision and rounding, transaction invariants, order or payment state machines, retries and ambiguous outcomes, WebSocket or event-stream correctness, fills and fees, balances and positions, reconciliation, recovery, auditability, or failure handling. Focus on concrete failure scenarios, broken invariants, and tests rather than generic style advice.
---

# Trading System Correctness Review
**Author:** Alex Chang (herefindalex@gmail.com)
**Created:** 2026/09/09
**Focus:** Financial transaction and trading-system correctness
**GitHub:** https://github.com/herefindalex
**License:** MIT

Review financially critical and real-time systems for correctness under partial failure, concurrency, retries, stale data, duplicated events, restarts, and precision boundaries.

The user's explicit instructions take precedence over this skill.

## Objective

Do not ask only whether the code works on the happy path.

Determine whether the system can preserve or recover the truth when:

- numeric values cross precision domains;
- totals and details can disagree;
- requests time out after remote side effects;
- orders or payments transition concurrently;
- events arrive late, duplicated, stale, or out of order;
- a process stops between receiving evidence and persisting its effect;
- local state drifts from external state.

A successful API response, a plausible number, a connected WebSocket, and a green health check are not by themselves evidence of correctness.

## Review Principles

### 1. Find invariants before finding bugs

Identify relationships that must always hold.

Examples:

```text
Sum(line item net amounts) = order net amount

Sum(allocated discounts) = order-level discount

Sum(execution quantities) = confirmed filled quantity

Original quantity = executed quantity + open quantity + terminal unexecuted quantity

Recorded accounting effects must be reconstructible from durable execution records
```

Adapt invariants to the actual domain. Do not impose an example invariant when taxes, amendments, fees, corrections, contract multipliers, or other domain rules make it invalid.

When a finding does not violate a single field but breaks a relationship between fields, state the broken relationship explicitly.

### 2. Distinguish exact arithmetic from correct semantics

Do not reduce numeric review to "use Decimal instead of float."

For every monetary, price, quantity, fee, or exposure value, determine:

- unit and currency/asset;
- price type, if relevant;
- allowed input increment;
- calculation precision;
- settlement or ledger precision;
- rounding mode and direction;
- the exact boundary where quantization occurs.

Look for scale propagation.

For example:

```text
price      = 0.01
quantity   = 0.015
notional   = 0.00015
```

Both inputs may be valid while the product requires a finer scale.

Also inspect chained calculations:

```text
price × quantity × fee_rate
```

Do not assume that price tick size determines notional or fee precision.

Flag generic code such as:

```go
amount := math.Round(price*qty*100) / 100
```

unless the two-decimal boundary and rounding rule are correct for that specific domain.

Do not recommend a generic epsilon comparison for domain values without explaining why the tolerance represents a valid business rule. Prefer explicit tick, step, decimal, fixed-point, or integer-unit semantics where appropriate.

### 3. Review rounding boundaries, not only rounding functions

Check whether the system rounds:

- after every pricing or discount stage;
- only at settlement;
- before or after allocation;
- before or after fee calculation;
- before or after quantity multiplication.

Different boundaries can produce different valid-looking numbers.

A later stage must not silently alternate between a higher-precision intermediate value and an already-quantized business amount.

For allocation logic, require deterministic remainder handling. A correct aggregate amount can still hide incorrect detail allocation.

Never reconstruct accounting truth from a rounded display-only value when the original allocation or higher-precision basis is available.

### 4. Separate command state from confirmed business state

An order, payment, transfer, or cancellation is not an API call.

Do not infer:

```text
HTTP 200 = filled
cancel request accepted = cancelled
timeout = failed
```

Model separately when useful:

- last confirmed business state;
- pending command or request;
- confidence or knowledge state;
- reserved risk/capacity while unresolved.

For trading orders, inspect whether transitions such as these are possible when supported by the venue:

```text
Accepted → PartiallyFilled → Filled
Accepted → Cancelled
PartiallyFilled → Cancelled
CancelPending → Filled
```

Do not reject a confirmed remote outcome merely because it conflicts with the client's last requested action.

### 5. Treat timeout as uncertainty unless the protocol proves otherwise

When a request can create a remote side effect, ask:

> Could the remote system have completed this operation even though the caller did not receive the response?

If yes, an immediate retry may duplicate the operation.

Require the design to explain:

1. the durable identity of the logical operation;
2. the identity of each submission attempt;
3. the remote identifier or correlation field;
4. the documented duplicate/idempotency semantics;
5. how an ambiguous outcome is resolved;
6. what risk or capacity remains reserved while resolution is incomplete.

A client order ID, request ID, or label is not automatically an idempotency contract. Verify the actual API semantics before recommending retry behavior.

If the outcome cannot yet be proven, preserve uncertainty instead of converting it to convenient failure.

### 6. Review concurrency at the decision boundary

Backend validation is not sufficient if multiple requests can consume the same capacity concurrently.

Inspect whether the check and reservation are consistent within the relevant scope for:

- available balance;
- max position;
- max order amount;
- inventory;
- discount budget;
- credit limit;
- risk limit.

Look for time-of-check/time-of-use races.

A UI validation is never the final correctness boundary for a financially consequential operation.

### 7. Connected is not the same as current or complete

For WebSocket, event-stream, and market-data paths, distinguish:

- transport connectivity;
- last message activity;
- last valid domain event;
- sequence/version continuity;
- event age or lag;
- local-state validity.

A socket that is still connected can carry stale, incomplete, or unusable state.

Do not apply a universal snapshot/delta recovery recipe. First determine the actual protocol:

- how snapshots are versioned;
- how deltas reference prior versions;
- whether sequence gaps can be detected;
- whether buffering and replay are supported;
- what reconnect guarantees exist.

If continuity cannot be proven, invalidate the dependent local state until the protocol-specific recovery completes.

### 8. Make duplicate and out-of-order processing harmless where required

Identify stable event or execution identities and their scope.

Check whether replay or reconnect can:

- apply an execution twice;
- regress an order from a terminal state;
- apply an older balance after a newer balance;
- produce duplicate ledger effects;
- re-trigger a trading signal that should be one-shot.

Memory-only deduplication is insufficient when correctness must survive process restart.

When ordering matters, identify the authoritative version, sequence, timestamp, or state-transition rule. Do not assume arrival order is business order.

### 9. Keep different truths separate

Do not collapse these concepts:

```text
Order       = what was requested
Execution   = what actually traded
Fee         = a separate accounting effect with an amount and asset
Balance     = assets held under an account model
Position    = exposure under an instrument/account model
```

A filled quantity does not necessarily equal a balance increase.

A single order can have multiple executions.

A fee can be charged in base asset, quote asset, settlement asset, or another asset depending on the venue and product.

For derivatives, preserve the semantics needed to interpret:

- linear vs inverse contracts;
- contract multiplier;
- amount/quantity unit;
- settlement asset;
- long/short or hedge mode;
- cross/isolated margin where relevant.

A common multi-venue model is useful only if it does not erase facts needed for correctness.

### 10. Treat missing, zero, and invalid as different states

Flag code that turns parse failure or missing data into a valid-looking zero.

For example:

```go
price, _ := strconv.ParseFloat(raw, 64)
```

Ask what `0` means in that domain.

Distinguish, where applicable:

```text
0
missing
not yet observed
stale
invalid
parse failure
not applicable
```

Financial and risk paths should fail according to an explicit policy rather than silently invent a usable value.

### 11. Review timestamp semantics

A field named only `timestamp` is often insufficient.

Where relevant, distinguish:

```text
exchangeTimestamp
receivedAt
processedAt
```

Check whether the code is measuring:

- remote event time;
- local receipt time;
- processing time;
- elapsed duration.

Use monotonic time for same-process elapsed durations when the runtime supports it.

Do not claim network or cross-machine latency by subtracting wall-clock timestamps unless clock synchronization and timestamp definitions justify the comparison.

### 12. Recovery must rebuild evidence, not only memory

A restart routine that loads a snapshot proves only that a snapshot can be loaded.

Review what can happen between the snapshot and recovery:

- fills;
- cancellations;
- new open orders;
- ambiguous submissions;
- balance changes;
- position changes;
- missed stream events.

Where the external venue/provider is authoritative, reconciliation may need to compare local state with relevant external evidence such as:

- open orders;
- order/payment history;
- recent executions or transactions;
- balances;
- positions;
- ledger entries.

Do not assume these endpoints form one atomic snapshot. Check account, instrument, unit, and time-window compatibility.

### 13. Reconciliation must explain drift

Flag reconciliation that merely overwrites:

```go
localPosition = exchangePosition
```

unless silent replacement is explicitly the intended policy and the evidence remains auditable.

When local and external state disagree, ask:

- Was an event missed?
- Was an event applied twice?
- Did another authorized actor change the account?
- Are the observations from different times?
- Are the units or account scopes different?
- Is one source derived from incomplete history?

Preserve enough evidence to explain the correction.

Do not automatically send a trade merely to force external state back to a local target. Resolving what happened and deciding to change exposure are separate operations.

### 14. Preserve uncertainty in risk decisions

If an operation may exist remotely but its outcome is unresolved, verify what happens to:

- reserved cash;
- reserved inventory;
- position capacity;
- order limits;
- duplicate-prevention state.

Releasing all reservations immediately after timeout can allow the system to exceed intended limits if the original operation later proves successful.

Prefer an explicit unresolved/degraded state with documented restrictions.

### 15. Require an audit trail that reconstructs causality

For important transactions, verify that the system can connect:

```text
logical intent
→ validation/risk decision
→ request attempt
→ remote acknowledgement
→ state observations
→ executions
→ fees
→ accounting effects
→ reconciliation
```

Important identities should survive across REST, WebSocket, persistence, retry, and recovery paths.

Logs such as:

```text
order success
ws update
done
```

are not enough to reconstruct why the system reached its current state.

## Required Failure Scenarios

When reviewing a relevant system, actively reason through at least the scenarios that apply:

```text
1. Response lost after remote operation succeeds.
2. Cancel and fill occur concurrently.
3. Partial fill occurs before cancellation.
4. Same execution/event is delivered twice.
5. Older event arrives after newer state.
6. WebSocket remains connected but required data becomes stale.
7. Sequence/version continuity is broken.
8. Process stops after receiving an event but before durable accounting is complete.
9. Process stops after durable event recording but before projection/state update.
10. Local state differs from external state after restart.
11. Price/quantity multiplication expands required decimal scale.
12. Aggregate amount is correct but detail allocation does not reconcile.
13. Rounded display value cannot reconstruct the underlying line/accounting amount.
14. Two concurrent requests both pass the same balance/risk check.
15. Missing or parse-failed data is interpreted as zero.
```

Do not manufacture findings merely because a scenario is listed. Verify whether the existing design already handles it.

## Review Workflow

### Step 1 — Establish scope

Identify:

- system component under review;
- authoritative external systems;
- monetary/asset units;
- instrument or transaction types;
- source-of-truth records;
- persistence boundaries;
- event sources;
- relevant API contracts.

If essential semantics are missing, mark them as unknown. Do not silently substitute generic exchange or payment-provider behavior.

### Step 2 — Extract invariants

Write down the key relationships the implementation must preserve before judging code.

Prefer a small set of strong invariants over a long generic checklist.

### Step 3 — Trace one transaction end to end

Follow at least one operation across:

```text
input
→ normalization
→ validation/risk
→ persistence/reservation
→ external request
→ acknowledgement
→ asynchronous updates
→ accounting/projection
→ reconciliation/recovery
```

Mark where truth can be lost, duplicated, rounded, reordered, or left ambiguous.

### Step 4 — Inject failures mentally or with tests

For each important boundary, ask what happens if the process, network, provider, or stream fails immediately before or after it.

Prefer concrete failure sequences over abstract claims such as "not resilient."

### Step 5 — Inspect recovery

Determine whether the system can distinguish:

- confirmed state;
- derived state;
- stale state;
- unknown state;
- reconciled state.

Verify that a restart does not declare itself healthy merely because connections were re-established.

### Step 6 — Recommend the smallest correctness-preserving change

Do not redesign the entire architecture when a local invariant, durable identity, state field, transaction boundary, or recovery step is sufficient.

When a larger redesign is actually required, explain which invariant cannot otherwise be guaranteed.

### Step 7 — Define a test for every important finding

A correctness finding is incomplete without a way to demonstrate the failure and verify the fix.

Prefer:

- property-based tests for numeric/allocation invariants;
- replay/idempotency tests;
- concurrency tests;
- fault injection;
- crash-boundary tests;
- state-machine transition tests;
- stale/gap stream tests;
- reconciliation fixtures.

## Finding Format

For each material issue, report:

```markdown
### [Severity] Short finding title

**Location:** file:line, component, or workflow stage

**Invariant / contract:** The relationship or external guarantee that must hold.

**Finding:** What the implementation currently does.

**Failure scenario:** A concrete sequence that produces an incorrect or ambiguous result.

**Impact:** Financial, risk, accounting, execution, recovery, or trust consequence.

**Recommended correction:** The smallest change that preserves the required semantics.

**Verification:** A test, assertion, replay, or failure-injection case that proves the correction.
```

If the external protocol behavior is not established, add:

```markdown
**Unknown to verify:** Exact venue/provider behavior required before choosing the fix.
```

Do not present an undocumented assumption as a fact.

## Severity Guidance

Use severity based on correctness impact, not coding style.

- **Critical** — Can create unintended financial transactions, duplicate orders/payments, materially wrong exposure, or unrecoverable accounting corruption.
- **High** — Can produce incorrect balances, fills, allocations, risk decisions, or recovery state under plausible production failures.
- **Medium** — Can create stale/ambiguous state, reconciliation drift, or audit gaps that require manual intervention but have a bounded direct impact.
- **Low** — Defensive improvement with limited correctness impact or an issue requiring an unlikely sequence.

Do not inflate severity merely because the component is financial.

## What Not to Do

Do not:

- equate e-commerce, payment, and trading domains; transfer engineering principles, not unsupported domain claims;
- recommend floating-point epsilon as a universal financial comparison;
- assume Decimal solves business rounding or allocation policy;
- assume a client-generated ID provides idempotency;
- assume HTTP success means a business operation is complete;
- assume timeout means failure;
- assume cancel acknowledgement means nothing filled;
- assume WebSocket connected means data is healthy;
- assume all venues use the same sequence, snapshot, quantity, fee, or position semantics;
- infer balance changes directly from order status when executions and fees are available;
- silently reconcile by overwriting unexplained drift;
- make latency claims from incompatible clocks;
- claim correctness from happy-path tests alone;
- invent venue guarantees, benchmarks, or production incidents.

## Completion Criteria

A review is complete when it can answer, for the requested scope:

1. What are the important correctness invariants?
2. Which state is authoritative, derived, stale, or potentially unknown?
3. Where are numeric precision and quantization boundaries defined?
4. What happens after an ambiguous external request?
5. How are duplicate and out-of-order events handled?
6. Can orders/transactions be reconstructed from executions or ledger evidence?
7. Can the system recover after restart without guessing?
8. Can local and external state be reconciled without hiding drift?
9. Can a reviewer reconstruct causality from the audit trail?
10. Is every material finding backed by a concrete failure scenario and a verification test?

The goal is not to prove that failure is impossible.

The goal is to make uncertainty explicit, preserve enough evidence to recover the truth, and keep related financial state consistent without guessing.