# Money Correctness Review

## Scope and outcome

- Target/repository:
- Revision or design version; base/head when reviewing a change:
- Requested workflows and permitted actions:
- Inspected paths/documents:
- Local changes preserved:
- Summary of verified defects, suspected risks, policy ambiguities, and evidence gaps:
- Most consequential remaining uncertainty:

Do not claim a whole-system audit from a narrow review. Put consequential findings next, then supporting detail. For a small PR, combine empty sections rather than padding the report.

## Findings

### MCR-001 — [Specific failed guarantee]

**Classification:** verified defect / suspected risk / policy ambiguity / evidence gap.

**Evidence:** POLICY / REPORTED / STATIC / LOCAL-TEST / DB-TEST / PROVIDER-EVIDENCE / PROD-EVIDENCE. For a verified defect, distinguish static proof from executed reproduction.

**Impact and priority:** Describe the affected entitlement or decision; identify whether external money movement was observed, only possible, or prevented elsewhere.

**Invariant and policy authority:** MC-ID plus the target's actual rule.

**Location:** revision, file:line range, symbols, caller/wrapper, and linked evidence.

**Preconditions:** the state, concurrency, eligibility, policy, and environment required.

**Expected behavior:**

**Observed or statically established behavior:**

**Causal path and missing/incorrect enforcement:**

**Counterevidence checked:** caller locks, constraints, provider caps, alternate policy, or other explanations.

**Minimal remediation direction:** preserve existing policy and adjacent guarantees; distinguish recommendation from implemented fix.

**Verification oracle:** monetary result, attribution result, state result, and evidence result. Include exact command and result only if executed.

**Uncertainty and limits:** unresolved premises, unavailable evidence, release applicability, and scope of tests.

## Economic model and responsibility map

| Value/resource | Currency and unit | Economic type/source | Owner | Authority/policy | Settlement/reversal boundary |
| --- | --- | --- | --- | --- | --- |

Explain relevant provenance in both directions and the distinction between current balance, spendability, refundability, and recognized/settled amounts.

## Transition and commit map

| Transition | Actor/component | Admission/precondition | Protected resource | Commit/evidence | Retry/abort/unknown behavior |
| --- | --- | --- | --- | --- | --- |

Name coordination mechanisms and which writers participate. Do not substitute a diagram label such as “atomic” for an inspected protocol.

## Invariant coverage

| ID | Target policy | Enforcement location | Evidence | Status | Next falsifying check |
| --- | --- | --- | --- | --- | --- |

Status vocabulary: supported in scope / violated / policy unclear / not inspected / not applicable. Explain not-applicable entries.

## Provider contract and reconciliation

Include only for relevant workflows. Summarize intent/attempt/key/object/event identities, current contract evidence, replay/release decisions, capacity retention, child-operation outcomes, reconciliation membership and differences, and exception owner.

## Failure matrix and verification plan

Use the selected failure-matrix rows. Identify actual versus proposed environments, controlled schedules, and oracles. Do not report an upstream test as executed locally.

## Execution record

| Check | Revision/environment | Command or inspection | Status | Observed result / artifact |
| --- | --- | --- | --- | --- |

Use proposed / not run / executed-pass / executed-fail / blocked. Keep source inspection separate from runtime results.

## Policy ambiguities and rejected candidates

Record missing policies without filling them from the article. Briefly explain candidates eliminated by caller enforcement, constraints, a deliberate policy, or unavailable premises.

## Do not claim

State the specific limits of this review, for example:

- No verified issue in the inspected paths does not establish global correctness.
- A model test is not a database-concurrency or provider-integration test.
- A local duplicate financial record is not proof of external duplicate payment.
- An order-header snapshot does not establish line-item funding history.
- An external case is not proof that the same defect exists here.
- Recommended tests or fixes have not run or shipped unless explicitly recorded above.

## Next action

Name the single most useful next verification or remediation step, its owner, and prerequisite evidence. Avoid a generic request to redesign the platform.
