# Independent Fictional Examples: Writing Calibration, Not Test Results

Both companies, sources, and roles below are original fictional material. They are not real user job searches, actual model-run outputs, or cases included in evaluation counts. Material IDs apply only within this document.

## Example A: FableQueue, with fuller information

### Supplied material

A1: Product description. FableQueue provides a managed job-queue service, charging by workload and retention duration, with explicit replay and customer-isolation capabilities.

A2: JD. The Backend Lead owns the execution service, leads a four-person team, handles capacity planning, and jointly defines usage events with Billing. Final pricing authority is not stated.

A3: Another JD. The Billing Engineer owns billing aggregation and invoice corrections, calculating charges from events emitted by the execution service.

All three are complete supplied fictional texts. Customer counts, revenue, current incidents, and internal interviews are absent.

### Acceptable report excerpt

**Core interpretation:** This role also requires clarifying the boundary between execution semantics and billing events as well as leading API development. This interpretation follows from workload-based pricing and the division of responsibilities across the two JDs; it is not a known incident. [A1-A3]

**Company understanding:** Customers buy managed execution and replay, and charges depend on workload. Revenue, customer count, and growth stage are not provided. A four-person team does not establish total company headcount. [A1/A2]

**Hypothesis:** The lead may need to keep retry/replay behavior consistent with usage-event definitions.

**Evidence:** Replay is a product capability; Backend and Billing jointly define events, while Billing calculates invoices. [A1-A3]

**Work implications:** Teams need clear agreements on billing for successful, failed, and retried jobs. Otherwise reliable execution and explainable invoices may create different requirements. This is a constraint to address, not evidence of incorrect invoices today.

**Alternative explanation:** The event contract may already be mature and require maintenance only. The JD does not establish its current state.

**Support level:** Indirect support. A collaboration boundary can be inferred, but whether it requires building or maintaining remains unknown.

**Validation question:** Who currently settles usage definitions for retries and replay? How was the latest disagreement between Execution and Billing resolved? A stable contract would narrow the hypothesis to maintenance; a contract still to be established would support the building interpretation.

### Unsupported statements

The company frequently miscalculates invoices; Billing holds the backend team back; this role can decide pricing. None is supported by the materials.

## Example B: PaperStream, with limited information

### Supplied material

B1: Product excerpt. PaperStream is researching a collaborative document-review tool; pricing and customers are not disclosed.

B2: JD. A Senior Backend Engineer builds APIs, works with designers, and participates in requirements discovery. Team size, manager, funding, and traffic are not listed.

### Acceptable report excerpt

**Core interpretation:** The stated role combines backend implementation and requirements discovery, rather than only implementing finished specifications. Evidence is insufficient to establish whether the product is live or its revenue stage. [B1/B2]

**Hypothesis:** Requirements clarification may be part of the engineer's work rather than entirely delegated to a Product Manager.

**Evidence:** The JD explicitly includes requirements discovery and collaboration with designers. [B2]

**Work implications:** Clarify how much time involves users and who makes final tradeoffs.

**Alternative explanation:** A product process may already exist and simply include routine engineering participation. This does not establish the absence of a product role.

**Support level:** Participation in discovery has direct textual support; its depth and associated authority remain unknown.

**Validation question:** How did the most recent feature move from a user problem to a specification? Where did this engineer participate, and who decided what not to build?

**Unknowns:** Business model, payers, team size, current manager, and product maturity. Start with one useful hypothesis supported by the materials rather than filling three unsupported risks.

### Unsupported statements

There is no Product Manager; the company has no product yet; this is definitely zero-to-one work; the founders do not understand technology. Missing information is not evidence of absence.
