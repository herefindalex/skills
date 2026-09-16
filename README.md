# Codex Skills

[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](./LICENSE)

A growing collection of reusable [agent skills](https://learn.chatgpt.com/docs/build-skills) for evidence-based software reviews.

The skills currently focus on financial correctness: preserving monetary meaning, transaction invariants, attribution, and recoverability when systems face concurrency, retries, partial failure, stale data, or ambiguous external outcomes.

## Project status

This repository is actively maintained and will grow as new review workflows are developed. Each skill is usable independently, so you can install only the ones relevant to your work.

The skills contain review instructions, reference material, and templates. They do not require a runtime service or transmit repository data on their own. Any tools, tests, or external sources used during a review remain subject to the permissions and environment of the agent running the skill.

## Available skills

| Skill | Use it for | What it produces |
| --- | --- | --- |
| [`money-correctness-review`](./money-correctness-review/) | Pricing, wallets, payments, refunds, credits, settlement, and reconciliation | An economic model, scoped invariant assessment, calibrated findings, and a targeted failure-test matrix |
| [`trading-system-correctness-review`](./trading-system-correctness-review/) | Trading, execution, market data, event streams, balances, positions, fees, recovery, and other financially critical transaction systems | Concrete failure scenarios, broken invariants, focused corrections, and verification tests |

### Which skill should I use?

Use **`money-correctness-review`** when the central question is what money represents and whether its source, allocation, reversal, settlement, and audit evidence remain consistent. It is the more structured review and includes reusable templates and reference material.

Use **`trading-system-correctness-review`** when the system must preserve transaction truth across order state changes, external APIs, WebSockets, duplicated or reordered events, restarts, precision boundaries, and reconciliation.

For a trading or payment system where both scopes matter, start with the narrower business question. Invoke both skills only when you need both the monetary provenance review and the broader real-time transaction-system review.

## Compatibility

The repository follows the [Agent Skills](https://agentskills.io/) directory format. It is designed for Codex and uses the standard `SKILL.md` entry point, with optional `agents/`, `assets/`, and `references/` directories.

The skills are instruction-based and have no package or language dependency. Their effectiveness depends on the agent's access to the code, design documents, tests, and external contracts relevant to the requested review.

## Install

Codex discovers personal skills under `~/.agents/skills` and supports symlinked skill directories. Clone this repository, then link the skills you want:

```bash
git clone https://github.com/herefindalex/skills.git \
  "$HOME/.local/share/herefindalex-skills"
mkdir -p "$HOME/.agents/skills"

ln -s "$HOME/.local/share/herefindalex-skills/money-correctness-review" \
  "$HOME/.agents/skills/money-correctness-review"
ln -s "$HOME/.local/share/herefindalex-skills/trading-system-correctness-review" \
  "$HOME/.agents/skills/trading-system-correctness-review"
```

If you clone the repository elsewhere, replace `$HOME/.local/share/herefindalex-skills` with its absolute path. Codex normally detects skill changes automatically; restart it if a newly installed skill does not appear.

You can also ask Codex's built-in `$skill-installer` to install a skill directly from this GitHub repository.

For reproducible use in a team or automated environment, pin the repository to a reviewed commit instead of following `main` automatically.

## Use

Mention a skill explicitly in your prompt:

```text
$money-correctness-review Review this refund workflow and produce an evidence-backed report.
```

```text
$trading-system-correctness-review Review this order lifecycle for retry,
out-of-order event, precision, and recovery failures.
```

Codex may also invoke an installed skill automatically when the request matches its description. Explicit invocation is useful when you want to guarantee a particular review lens.

Both skills begin from the supplied repository, pull request, design, or workflow. They distinguish verified defects from suspected risks, policy ambiguities, and evidence gaps. They do not promise that a system is correct simply because no defect was found in the reviewed scope.

## Repository structure

```text
skills/
├── LICENSE
├── README.md
├── money-correctness-review/
│   ├── SKILL.md
│   ├── agents/openai.yaml
│   ├── assets/
│   └── references/
└── trading-system-correctness-review/
    └── SKILL.md
```

Each skill lives in its own directory and is defined by a `SKILL.md` file with `name` and `description` front matter. A skill may also include:

- `agents/openai.yaml` for display and invocation metadata;
- `assets/` for report templates and working artifacts;
- `references/` for detailed guidance loaded only when relevant;
- `scripts/` for deterministic tooling when instructions alone are insufficient.

## Adding another skill

Keep each skill focused on one review job and add it as a new top-level directory. At minimum:

1. Create `<skill-name>/SKILL.md`.
2. Add concise `name` and `description` front matter that clearly defines when the skill should trigger.
3. Write explicit steps, expected outputs, scope boundaries, and completion criteria.
4. Add optional resources only when they improve repeatability or keep `SKILL.md` focused.
5. Add the skill to the catalog and repository tree in this README.

## Contributing

Issues and pull requests are welcome. When proposing a new skill or changing an existing one:

- keep the skill focused on a clearly defined job;
- state when it should and should not trigger;
- separate verified facts, assumptions, and proposed guidance;
- include concrete outputs and completion criteria;
- keep examples synthetic and free of secrets or customer data;
- update this README when the catalog or directory structure changes.

For substantial changes, open an issue first to describe the use case and expected review workflow. By contributing, you agree that your contribution will be licensed under the repository's MIT License.

## License

This repository and every skill it contains are licensed under the [MIT License](./LICENSE). You may use, copy, modify, merge, publish, distribute, sublicense, and sell copies subject to the license terms and preservation of the copyright and permission notice.

The skills provide review workflows and guidance. They do not constitute financial, legal, accounting, or investment advice, and they do not guarantee that a reviewed system is free of defects.

## Author

Created and maintained by [Alex Chang](https://github.com/herefindalex).
