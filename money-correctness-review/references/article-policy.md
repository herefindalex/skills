# The article's wallet policy: a scoped case study

Source: Alex Chang, **A Balance Is Not Enough: Designing Money Correctness Across State Transitions**, supplied `article-source.md`. Source SHA-256: `05ebe5676ff0acd3f482d23039b19d5ccae4466d074f196fca08f1801d105d73`.

This file preserves the article's distinctions. It is not a generic payment policy, a tax rule, or a recommendation to reduce refunds in another product. Read it only when the reviewed system adopts the policy or when reviewing the article itself.

## Historical rules described by the author

- The first implementation already tracked funding lots to orders. It was not a repair of an anonymous-balance design.
- Each top-up carried customer-funded principal and linked promotional credit. Principal did not expire; unused promotional credit did.
- Eligible promotion was consumed before principal. Within each class the order was FIFO, not earliest-expiry-first.
- An order refund reversed recorded consumption. Restored promotion was usable if still valid and immediately expired otherwise. In either case, the reversed consumption no longer counted as ultimately used promotion.
- Account refunds were all-or-nothing closures, not partial principal withdrawals. The account was locked and the refund process waited for the relevant final order-refund deadline.
- Each funding lot had an independent cash-refund calculation and was explained independently to the customer. Account totals were sums of those results, not another calculation boundary.
- Cash was floored at each lot's currency-minor-unit boundary. Fractions were not pooled across lots.
- The promotion settlement and corresponding income/accounting treatment were handled after daily or month-end reconciliation. The article does not prescribe universal general-ledger entries.
- Attribution and refund calculations stopped at the order boundary. The **order portion** of each before/after operation snapshot serialized the **order header only**, not line items. This does not mean the commerce system had no line-item data.

## Exact case arithmetic

All inputs use the same currency and integer minor unit:

    P = original customer-funded principal, P > 0
    R = remaining principal, 0 <= R <= P
    C = promotional consumption not reversed by order refunds, C >= 0
    cash = (P * R) // (P + C)
    adjustment = R - cash

The numerical function alone does not establish ownership, input accuracy, refund eligibility, or C's relationship to the original grant history. Use checked/wide multiplication outside arbitrary-precision runtimes.

For a two-decimal currency:

    P = 100000, R = 55000, C = 10000
    cash = 50000
    adjustment = 5000

An untouched second lot with P = R = 100000 and C = 0 returns 100000. Total cash is 150000. Pooling first gives 147619, which violates this particular independent-lot policy despite balancing the aggregate remaining principal.

When C = 0, cash equals R. Unused expired promotion does not enter C. A refund that reverses promotion reduces C even if the restored grant immediately expires. Closing an unused grant must not be relabeled as consuming it.

For each lot:

    cash + adjustment = R
    0 <= exact_cash - cash < 1 minor unit

For explanation, retain exact inputs and the fractional remainder where needed. The integer adjustment includes the consequence of flooring; do not invent extra promotional consumption to explain that fraction.

## Reference extensions, not historical claims

The article proposes line-level economic decomposition and joint funding allocation, canonical refundable units/ranges, explicit admission/drain/seal coordination, durable intent fingerprints, outbox/evidence commit boundaries, provider-specific recovery, and approval-bound corrections.

Do not describe those proposed mechanisms as shipped historical technology. Do not infer PostgreSQL, Serializable, Kafka, full event sourcing, immutable object-store snapshots, double-entry accounting, maker-checker controls, or provider-specific adapters in the original system without separate evidence.

The historical partial-order-refund split was not reconstructed by the article. Its examples are not proof that the original system always used proportional reversal. Order-level attribution with a specified partial-refund rule can be a legitimate design.

## Two arithmetic traps retained from the article

**Scalar quantity allocation does not automatically compose across sources.** With total 4, quantity 3, and two funding sources of 2 each, the first unit's scalar budget is 1 while the separately floored funding sources total 0. Use jointly valid stored vectors, not independent formulas that disagree.

**Business history cannot be arbitrarily permuted.** Partitioning the same fixed set of returned units can preserve the aggregate reversal vector. Crossing promotion expiry can still change spendability. Do not promise that every permutation of spend, expiry, and refund has the same outcome.

## Article-to-skill mapping

| Article section | Review focus |
| --- | --- |
| 1–2: cash refund and independent top-ups | MC-01, MC-02, MC-05 |
| 3: order scope and snapshots | MC-05, MC-11 |
| 4: pricing and joint funding | MC-03, MC-04, MC-06 |
| 5: closure barrier | MC-08 |
| 6: local commitment and external attempts | MC-07, MC-09, MC-10, MC-11 |
| 7: reconciliation and corrections | MC-12 |
| 8: tests and limits | Evidence rules and failure matrix |
