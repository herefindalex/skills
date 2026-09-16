# Source register and claim boundaries

## Requested basis

The workflow and review questions were derived from the supplied English article:

**Alex Chang — A Balance Is Not Enough: Designing Money Correctness Across State Transitions**  
Subtitle: *What we built at the order boundary—and how I would extend it to line-item refunds.*

Local source name: `article-source.md`; SHA-256: `05ebe5676ff0acd3f482d23039b19d5ccae4466d074f196fca08f1801d105d73`.

The companion source file was `sources-and-validation.md`. No public article URL was supplied for this release; none is invented. The article itself is not copied into this skill, and the skill does not need that local path at runtime. Its relevant case boundaries are preserved in `article-policy.md`.

The skill adds an operational review workflow, finding classifications, report templates, and test planning derived from those ideas. These additions are not historical implementation claims.

## External research leads inherited from the article

These links are authoritative sources to reopen when relevant. Article status checks were dated September 15, 2026. **This skill release does not reverify these financial products or freeze their current status.** Do not quote a retention interval, release status, or root-cause claim from this list without checking its source for the target review.

| System | Source identity / direct URL | Bounded use |
| --- | --- | --- |
| Lago | [PR #4838 — feat(wallet): Add API endpoints for consumption/funding traceability](https://github.com/getlago/lago-api/pull/4838) | Feature example of bidirectional funding traceability, not proof of another wallet's policy |
| Magento | [Issue #38455 — Wrong Order total, the round is not applied to the price calculation.](https://github.com/magento/magento2/issues/38455); [PR #39687 — magento/magento2#38455: Fixed](https://github.com/magento/magento2/pull/39687) | Reported traversal-sensitive totals and inspected discount-rounding change; read actual tests before claiming permutation coverage |
| WooCommerce | [Issue #64668 — Refund amount can exceed original order total due to per-line tax rounding accumulation, with no UI warning or automatic correction](https://github.com/woocommerce/woocommerce/issues/64668); [PR #65732 — Fix/64668 refund rounding autocap](https://github.com/woocommerce/woocommerce/pull/65732) | Aggregate limits versus component representation; do not treat auto-cap as an accepted universal fix |
| Medusa | [Issue #16012 — Check-then-act races bypass amount guards in payment capture/refund and promotion budgets](https://github.com/medusajs/medusa/issues/16012); [PR #16097 — fix(payment,promotion): serialize concurrent money guards to prevent over-capture, over-refund and budget overspend](https://github.com/medusajs/medusa/pull/16097) | Inspect resource-scoped serialization and tests; distinguish internal admission from external payment |
| Stripe | [Billing credits](https://docs.stripe.com/billing/subscriptions/usage-based/billing-credits) | Grant restoration/expiry under a subscription-billing product, not generic wallet policy |
| Stripe | [Advanced error handling](https://docs.stripe.com/error-low-level); [Idempotent requests](https://docs.stripe.com/api/idempotent_requests); [Webhooks](https://docs.stripe.com/webhooks) | Recheck endpoint/version-specific uncertainty, replay, retention, and delivery contracts |
| Modern Treasury | [Verify Prior Ledger States](https://docs.moderntreasury.com/ledgers/docs/verify-prior-ledger-states); [Update Ledger Transaction](https://docs.moderntreasury.com/platform/reference/update-ledger-transaction) | Determine the precise versioning and financial-mutability boundary, including metadata exceptions |
| Modern Treasury | [Link a Ledger Transaction to an Expected Payment](https://docs.moderntreasury.com/ledgers/docs/link-a-ledger-transaction-to-an-expected-payment) | Referenced reversal/new pending state when reconciliation changes, within the documented integration |
| PostgreSQL | [Version 18: Transaction Isolation](https://www.postgresql.org/docs/18/transaction-iso.html) | Use the actual deployed version and transaction protocol, not a blanket claim that a transaction prevents races |
| Shopify | [FinancialSummaryDiscountAllocation](https://shopify.dev/docs/api/admin-graphql/latest/objects/FinancialSummaryDiscountAllocation) | Approximate per-item display is not a proof of a refund-allocation algorithm; pin API version |
| Yuno | [Authentication / idempotency](https://docs.y.uno/reference/getting-started/authentication); [Reconciliations](https://docs.y.uno/docs/using-yuno/dashboard-overview/reconciliations) | Reopen current contracts; do not carry forward earlier research assertions about 400/500 key storage |
| Adyen | [Refund](https://docs.adyen.com/online-payments/refund/) | Check method-specific asynchronous completion and later reversal behavior |

A review finding that uses an external case must additionally capture issue/PR status, exact revision, evidence of root cause or proposal, test limitations, and the invariant it supports. Analogy is not evidence that the same bug exists in the reviewed target.

## Packaging documentation checked for this skill

Checked September 16, 2026:

- [OpenAI — Build skills](https://developers.openai.com/codex/skills), redirected to [ChatGPT Learn — Build skills](https://learn.chatgpt.com/docs/build-skills): local Codex skill layout, `.agents/skills`, explicit `$skill-name` invocation, and optional `agents/openai.yaml` metadata.
- [Agent Skills specification](https://agentskills.io/specification): required `name`/`description`, directory matching, relative references, and progressive disclosure.

The primary `SKILL.md` uses only the portable required frontmatter. `agents/openai.yaml` is optional host metadata. Packaging validation is not proof that the workflow triggers reliably or finds defects in every agent runtime.
