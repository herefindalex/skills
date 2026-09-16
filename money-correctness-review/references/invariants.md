# Scoped invariant catalog

These are review questions derived from the article, not mandatory product policies. Record applicability, policy authority, enforcement, and evidence for each selected entry. A component can legitimately delegate a guarantee, but the delegation and the actual enforcing path must be established.

Use the IDs in findings, reports, and test plans. Do not mechanically mark a design defective because it has different terminology, permits authorized overdrafts, or intentionally stops attribution at the order boundary.

## MC-01 — Economic identity and source admission

**Question:** What kind of value is changing, for whom, and on what evidence?

Distinguish principal from promotion, discounts from tender, captures from authorizations, and gross from net settlement. Treat currency and unit as part of an amount's type. Do not net unrelated customers or currencies to make a total appear balanced.

Trace the rule that admits external funding. A pending request is not necessarily funded value; a credit-based product can admit earlier under an explicit risk contract. Confirm customer, currency, amount, reference, and operation identity before creating a funded lot. Check that duplicate completion paths cannot create another lot or grant.

**Falsifier:** Two completion observations for one top-up create two customer entitlements, or a goodwill credit is accidentally classified as cash-refundable principal.

**Do not infer:** A provider's “succeeded” status guarantees irreversible funding, or every credit must originate from a customer cash deposit.

## MC-02 — Precision and rounding boundaries

**Question:** Where is each amount authoritative, and who owns each remainder?

Find parsing, multiplication/division, conversions, storage, serialization, display, and provider payload boundaries. Record the policy, currency quantum, and intermediate precision at each one. Inspect overflow, truncation, signed values, and exact ties. For nonnegative integer minor units, integer quotient can implement floor without a binary-float intermediate; that is useful only when floor is the declared policy.

Do not flag every float occurrence. Trace whether approximation reaches a financial decision and show a numerical boundary or a missing contract. Likewise, Decimal is not proof: exact arithmetic can still implement the wrong decomposition.

**Falsifier:** Aggregate flooring replaces required lot-level flooring; both refund and adjustment round upward; a displayed approximate unit amount becomes the refund authority; a conversion overflows before division.

**Remainder rule:** Preserve the owning boundary and explanation. Do not transfer another lot's fraction into this lot. Do not label a sub-minor-unit flooring effect as additional promotion consumption.

## MC-03 — Deterministic pricing and composition

**Question:** Are equivalent economic inputs independent of incidental traversal?

Include rule priority, eligibility, business ordering, policy version, and canonical tie-breaks in the inputs. Preserve gross, reductions, taxes, fees, shipping, and payable totals with the appropriate signed decomposition. A displayed uniform unit price need not multiply to an allocated line budget without an explicit remainder.

Percentage composition is a policy: sequential and original-price-based discounts are not interchangeable. A correct payable amount can coexist with an incorrect reported effective discount rate.

**Falsifier:** Changing only database row enumeration changes the payable total or the selected remainder recipient despite unchanged canonical identities and policy.

**Do not infer:** FIFO lots, explicit discount priority, or different eligibility are incidental permutations.

## MC-04 — Joint allocation, eligibility, and feasibility

For a nonnegative funding matrix A, unit budgets V, source budgets W, and eligibility E:

    for each unit u:   sum_s A[u,s] = V[u]
    for each source s: sum_u A[u,s] = W[s]
    A[u,s] >= 0
    E[u,s] = false implies A[u,s] = 0

Use one currency/unit per matrix or an explicit conversion layer. Negative discounts belong to pricing; they are not negative funding sources. Validate feasibility before committing a payment plan.

Independent rounding can violate both margins. A useful synthetic counterexample is total value 4, quantity 3, promotion funding 2, and principal funding 2, all in integer minor units. The first scalar unit is worth floor(4/3) = 1, but independently flooring both sources gives 0 + 0.

A joint allocator may be deterministic and feasible without being proportional, fair, or optimal. Verify only the objective promised. Eligibility restrictions can require rerouting; greedy traversal is not automatically adequate.

**Falsifier:** Every unit balances but a source is over-allocated, or a balanced matrix spends a restricted promotion on an ineligible unit.

## MC-05 — Provenance and explanation

**Question:** Can the explanation use the actual attribution rather than reconstructing a convenient one?

Follow source → consumption → order or refundable unit, and the inverse queries. Reconcile projections to the same version/cut of history. Keep estimates distinguishable from sealed results. Preserve versioned calculation inputs where they govern later explanation.

Order-level attribution can support an explicit partial-refund allocation policy. Absence of per-item funding is not by itself a defect. The defect would be a stronger claim—such as asserting a historical line allocation that was never recorded—or inability to satisfy the product's actual reversible-unit contract.

**Falsifier:** The customer statement and execution plan independently recompute different refund amounts; an old order is attributed to a newly deposited lot during reconstruction.

## MC-06 — Referenced and bounded reversals

**Question:** What original movement is reversed, by how much, and to which source?

For each original eligible edge or budget, with mutually exclusive completed and unresolved buckets:

    completed_reversal + unresolved_commitment <= original_reversible_budget

For a new request n, verify the same inequality including n at admission. Successful movement and reservation must not be counted twice. A pending provider object and an unknown transport result can describe the same commitment.

Do not rerun current FIFO to discover the source of an old refund. Use recorded attribution or a documented order-level reversal policy and preserve its result. Handle unexpired restoration, expired restoration, and any expressly separate replacement grant. Reversing consumption and restoring spendability are distinct effects.

For amount-only refunds or quantity returns, inspect repeated partial operations, caps, terminal remainders, and identity reuse. State exactly which business unit the refund selects.

**Falsifier:** A repeated refund restores an edge twice, or a refund restores promotional value as principal without an authorized economic conversion.

## MC-07 — Shared-resource concurrency

**Question:** Which shared capacity does the decision consume, and what serializes all writers?

Identify the linearization point and inspect read/validate/write, current-state refresh, conditional writes, constraints, uniqueness, transaction scope, and locks. Check every caller and administrative path. A cart lock does not necessarily serialize a shared campaign budget; locking a child does not necessarily protect a parent-level sum.

For a guarded update, inspect affected-row handling. For a row lock, inspect the transaction lifetime and the reread. For optimistic control, inspect the version predicate and failure handling. For Serializable, inspect full local-transaction retries. An ORM cache can defeat the intended fresh read.

**Falsifier:** Two locally admitted reversals each observe the same remaining capacity and their committed sum exceeds it.

**Impact boundary:** Local duplicate records or over-admission do not prove the provider paid twice. A provider cap can prevent an external overpayment while internal state is still inconsistent.

## MC-08 — Closure admission, draining, and sealing

**Question:** Which operations may still change settlement inputs, and how is their completion known?

A business account lock differs from a database lock. It may refuse new exposure while permitting accepted refunds, expiry, reconciliation, and late funding observations. Identify the contract for each permitted writer.

Passing the last relevant refund deadline closes new admission; it does not establish that admitted work has drained. Use durable accepted-operation records and completion evidence, not just queue depth. Inspect extended deadlines and in-flight top-ups too.

At sealing, coordinate admission, drain verification, input version, and snapshot commit. In one database, every relevant writer must share the protocol. Across services, a local row lock cannot replace a durable fence/acknowledgement covering admitted work. For large accounts, versioned or fenced calculation must still establish the same stable cut.

**Falsifier:** A legally admitted order refund commits after sealing without being included or explicitly handled, changing the lot inputs under an immutable-looking result.

**Do not infer:** Closing the customer return window removes all future payment-rail reversal or dispute risk.

## MC-09 — Intent, fingerprint, attempt, and observation

**Question:** Are distinct identities serving distinct purposes?

Map business intent ID, relevant request fingerprint, provider attempt/key, provider payment/refund IDs, inbound event ID, and reconciliation record ID. Scope identities to the appropriate tenant/account/provider/operation.

The same intent with a materially different amount, currency, destination, unit selection, or economic type must not silently overwrite the original. Do not deduplicate legitimate equal-amount partial refunds by amount alone. Do not deduplicate every refund by original payment ID alone.

**Falsifier:** Retrying an unresolved operation deletes its identity and creates a fresh operation; a transport retry is counted as another business refund.

**Limit:** Stable identity is necessary for many designs but does not itself guarantee exactly-once external effects. The external contract and recovery protocol still matter.

## MC-10 — Uncertainty, recovery, and delivery

**Question:** Which evidence permits replay, release, success, or failure?

Distinguish not sent, provider accepted/pending, processed, definitively not effected, and unknown. A timeout or cached error is not proof of no side effect. A worker lease expiring does not cancel the old request. Track retries as attempts of the same intent, using provider-specific contracts.

Persist incoming observations and correlate before applying effects. Validate allowed transitions rather than assigning status from arrival order or a simplistic status rank. Verify event authenticity when applicable. Duplicate delivery and different events describing the same economic effect need separate reasoning.

**Falsifier:** Side effect happens, response is lost, and recovery either creates another intent or makes the reserved capacity spendable again.

**Operational requirement:** Unresolved is a valid safety state, but needs an owner, aging threshold, evidence source, and next action—not indefinite silent abandonment.

## MC-11 — Evidence scope, atomicity, and retention

**Question:** What can the retained evidence actually explain?

Separate monetary movements, funding relationships, object snapshots, actor/reason context, and external observations. Identify which objects/fields are captured and at what version. Do not infer line-item history from an order-header snapshot, event sourcing from snapshots, or tamper resistance from append-only application conventions.

Check consistency between a committed mutation and its durable evidence. After-commit publication can avoid publishing rolled-back work but is not by itself a durable outbox. A later “after” read can capture someone else's change. Rejected attempts must not masquerade as committed monetary movements.

Consider actor identity, reason, schema version, correlation, redaction, access, retention, and explicit completeness for large bundles. Preserve financial evidence without copying secrets indiscriminately. A log or snapshot can record an incorrect transition; it does not certify it.

**Falsifier:** Financial state commits but the only audit record can be lost in a process crash, or the snapshot silently omits fields needed to support the claimed explanation.

## MC-12 — Reconciliation, corrections, and control changes

**Question:** Do the internal calculation, provider facts, settlement records, and accounting disposition agree at their stated boundaries?

Keep lifecycle dimensions distinct. Match identity before classifying differences. A tolerance can select candidates without authorizing an unexplained write-off. Compare batch members as well as totals. Give imports and corrections stable identities; reimport must not remint money.

A missing movement and a duplicate of equal size can leave a batch total unchanged. An unresolved or ambiguous match should remain explicit. Known fees, tax, conversion, reversals, and rounding dispositions need their own documented treatment and precision.

Corrections must preserve the fact that the earlier financial state existed. Distinguish allowed metadata edits from rewriting posted amounts or source links. Classify goodwill separately from principal correction. Where required, bind approval to payload and relevant versions; revalidate at execution. Changes to rules and permissions capable of moving money also need controlled history.

**Falsifier:** A successful local refund is labeled financially complete without required external evidence, a batch reimport duplicates an adjustment, or an approved payload changes destination without renewed approval.

**Limit:** This review does not certify accounting recognition, tax compliance, legal refund rights, or an organization's controls. Record the authority required for those decisions.
