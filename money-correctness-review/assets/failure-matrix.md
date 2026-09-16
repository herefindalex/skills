# Selective failure matrix

Copy only applicable rows into a review. All rows below are **proposed**, not executed. Adapt the oracle to the actual target policy and make the monetary, attribution, and evidence outcomes explicit.

| ID | Boundary / synthetic schedule | Required observation | Related invariants |
| --- | --- | --- | --- |
| FM-01 | Deliver two completions for one top-up | One admitted principal lot and linked grant, or the documented deduplication result | MC-01, MC-09 |
| FM-02 | Two spends contend for the last available budget | Committed consumption respects the actual capacity; losers are rejected or retried | MC-07 |
| FM-03 | Different carts consume one shared promotion budget | Serialization covers the shared budget, not merely each cart | MC-07 |
| FM-04 | Spend and promotion expiry meet at the cutoff | Eligibility follows the declared temporal policy and one coordinated outcome | MC-02, MC-06, MC-07 |
| FM-05 | Permute incidental order/source enumeration | Same result under identical stable IDs, priority, eligibility, and policy | MC-03, MC-04 |
| FM-06 | One line: value 4, quantity 3, sources 2 and 2 | Unit and source margins both balance; independent floor shortcut is rejected | MC-04 |
| FM-07 | A restricted source competes with a flexible source | Allocation respects eligibility and either finds a feasible plan or explicitly rejects | MC-04 |
| FM-08 | Refund the same fixed units in one batch and several | Same aggregate reversal vector under the same policy; expiry effects considered separately | MC-06 |
| FM-09 | Two refunds compete for the same edge/unit | Completed plus unresolved allocations never exceed the original budget | MC-06, MC-07 |
| FM-10 | Restore a consumed grant after its expiry | Original consumption reverses; restored availability follows expiry policy | MC-05, MC-06 |
| FM-11 | Deadline passes with an accepted refund still unresolved | Settlement does not seal prematurely | MC-08 |
| FM-12 | Last permitted refund admission races with sealing | One coordinated outcome includes the work or rejects admission; no unaccounted mutation | MC-07, MC-08 |
| FM-13 | A top-up initiated before closure confirms later | Money admission/return/exception is recorded; lock does not discard the obligation | MC-01, MC-08 |
| FM-14 | Crash after intent commit, before dispatch | Resume the same intent and plan, without recomputing a different entitlement | MC-09, MC-10 |
| FM-15 | Fake provider acts, then loses the response | Preserve unknown outcome, identity, and capacity; no blind replacement operation | MC-09, MC-10 |
| FM-16 | Worker lease expires while old send remains in flight | Replacement does not assume expiry cancelled the external side effect | MC-10 |
| FM-17 | Redeliver and reorder equivalent provider observations | No duplicate effect; valid state graph and reconciliation determine outcome | MC-09, MC-10 |
| FM-18 | Child A succeeds, B is unknown, C rejects | Parent retains partial progress and obligations; no blanket rollback or success | MC-09, MC-10, MC-12 |
| FM-19 | Durable audit/outbox write fails before local commit | Reference protocol aborts monetary mutation; report actual target contract | MC-11 |
| FM-20 | Audit publication fails after durable local evidence exists | Evidence persists and publication can resume without reminting money | MC-11 |
| FM-21 | Reimport the same settlement batch | Import identity prevents repeated financial effects | MC-09, MC-12 |
| FM-22 | Batch totals match but a member is missing and another duplicated | Membership discrepancy stays visible | MC-12 |
| FM-23 | One external movement matches two candidates | Ambiguity remains explicit until attribution is established | MC-05, MC-12 |
| FM-24 | Amount/destination changes after approval | Approval is invalidated or explicitly reevaluated under the target policy | MC-12 |
| FM-25 | Earlier positive refund evidence is followed by a reversal | Append linked recovery/correction facts; preserve sealed history | MC-10, MC-12 |
| FM-26 | Sealed account receives an administrative monetary correction | Explicit permitted correction path; no silent rewrite of final inputs | MC-08, MC-12 |

For each selected row record: target revision, preconditions, controlled boundary, expected state/amount/source/evidence, required harness, authorized scope, status, observed result, and the limits of the result. Never perform fault injection against real payment systems as part of this skill.
