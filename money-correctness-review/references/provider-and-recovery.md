# Provider contracts, operation recovery, and closure

Use this only when the reviewed path crosses a provider, bank, asynchronous service, or multi-step workflow. This is a review protocol, not an external-execution tool.

## Separate identities before prescribing retries

For each path identify:

- Business intent: the durable request whose economic effect is wanted.
- Request fingerprint: relevant customer/account, currency, amount, destination, selected units, and operation type.
- Execution plan: how one or more external movements realize the intent.
- Transport attempt: a particular send or retry.
- Provider idempotency scope/key and its binding to request parameters.
- Provider payment/refund/payout object identity.
- Inbound observation/delivery identity.
- Reconciliation import and settlement record identity.

One business operation may have several attempts or several required child movements. Several legitimate partial refunds may share one payment and the same amount. Neither correspondence is necessarily one-to-one.

Fill the provider-contract template from the exact endpoint, version, payment method, account scope, and available documentation. Do not infer behavior from HTTP status names alone.

## Classify evidence, not exceptions

| Observation | Review interpretation |
| --- | --- |
| Local transaction did not commit | No committed local intent from that transaction; separately check whether any external work was wrongly sent before commit |
| Intent committed, dispatcher has not sent | Resume durable work subject to current authorization and the stored plan |
| Request may have reached provider, no definitive response | Unknown external outcome; retain identity and consumed capacity |
| Provider accepted asynchronous processing | Accepted is not necessarily completed or irrevocable |
| Documented final rejection with no side effect | Eligible for explicit resolution/replanning; business policy decides whether to keep commitment or cancel |
| Provider reports completion | Record the observation; determine what further settlement/accounting evidence the product requires |
| Later reversal/return | Append the new linked financial fact; do not erase the earlier observation or sealed calculation |

Do not convert repeated timeouts into evidence of failure. Do not rotate a key solely because it failed twice. A cached failure may coexist with a side effect under some provider contracts. Conversely, do not assume reusing a key always replays a result forever.

## Safe release is a positive decision

A capacity release needs contract-backed evidence or a local proof that no external side effect could have occurred. “No success row,” elapsed worker lease, expired retry timer, or absent webhook are insufficient by themselves.

The parent intent may remain pending even when an individual attempt definitively fails. A financial product can choose to retain the commitment while changing the execution route. Do not automatically reopen an account or restore its spending balance from a child-attempt failure.

If a prior attempt succeeded and another child is unresolved, never roll back all child records as though no money moved. Track required, completed, pending, unknown, and failed children without double counting. Reconcile the execution plan back to its lot or order entitlements.

## Closure review

Review account locking, accepted work, deadline evaluation, sealing, and external execution as separate phases.

- Stop new economic exposure according to policy; keep paths for existing obligations and external observations.
- Establish the maximum relevant refund deadline under each order's policy, rather than assuming the newest order has the latest deadline.
- Drain all accepted unresolved work that can affect the result, including previously initiated top-ups where applicable.
- Seal a consistent input version while excluding ordinary late admission through the same coordination protocol.
- Preserve the sealed calculation during recovery. A retry resumes it rather than rereading mutable balances and calculating a different amount.
- Distinguish a normal customer return deadline from future chargeback, bank return, or provider-reversal risk.

A local lock does not prove cross-service drain. Require a documented durable fence, acknowledgement, or equivalent protocol with a coverage boundary. Never infer remote completion merely from silence or an empty queue.

## Manual intervention

Review corrections as typed operations. Bind approval, where required, to a specific payload and relevant state version. Revalidate at execution. Separate requester/approver where policy requires it. Do not treat approval as evidence that a financial precondition is satisfied.

Manual goodwill must not silently become customer-funded principal. Financial history correction needs a reference and reason; allowed metadata editing has a narrower contract. Changing a policy or approver rule that can enable money movement is itself control-sensitive work.

## Evidence retention and escalation

Capture the relevant request parameters or protected fingerprint, endpoint/version, timestamps, provider IDs, status observations, verification basis, and corrections. Redact secrets and unnecessary personal data. Remote request logs with finite retention do not replace local durable financial history.

For an unresolved result specify the owner, next authorized lookup/evidence source, aging threshold, and escalation. This skill may recommend these steps but must not send live refunds, query private financial accounts, or make approval decisions.
