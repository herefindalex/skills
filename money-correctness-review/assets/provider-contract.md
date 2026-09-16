# Provider Contract Record

Fill this from current primary documentation and inspected adapter behavior. Unknown fields stay unknown; a missing contract is not an invitation to choose a convenient retry policy.

## Scope

- Provider, account/region, payment method/rail:
- Operation and endpoint:
- API/SDK version and adapter revision:
- Primary source URL(s), section, and checked date:
- User-supplied contract or retained provider evidence:

## Identity and capacity

- Durable business intent and request fingerprint:
- Child execution plan and amount/source mapping:
- Provider key scope, retention, and parameter binding:
- Provider payment/refund identity:
- Event/delivery identity and financial effect deduplication:
- Capacity owner and representation of unresolved attempts:

## Outcomes and permitted recovery

| Observation | Documented meaning | Side effect excluded? Evidence | Permitted replay/lookup | Capacity disposition | Local behavior |
| --- | --- | --- | --- | --- | --- |
| Not dispatched | | | | | |
| Validation rejection | | | | | |
| In-progress duplicate | | | | | |
| Timeout / connection loss | | | | | |
| Server failure | | | | | |
| Accepted asynchronously | | | | | |
| Completed | | | | | |
| Later failure / reversal | | | | | |

Do not assume an HTTP status alone decides the third column. Do not merge provider-defined failure with locally unknown transport outcome.

## Recovery and evidence

- Authority for current status; consistency/visibility limitations:
- Safe key reuse conditions:
- Conditions, if any, permitting a new key under the same tracked intent:
- Handling after key-retention expiry:
- Response-to-durable-acknowledgement crash window:
- Worker-lease and stale-worker behavior:
- Webhook verification, durable receipt, duplicate and unordered delivery:
- Required provider/settlement/bank/accounting evidence:
- Unknown owner, aging threshold, escalation, and next authorized action:

## Verification boundary

- Code paths and tests inspected:
- Local fake semantics, especially side-effect-then-response-loss:
- Executed checks and raw results:
- Proposed checks only:
- External interactions not performed:
