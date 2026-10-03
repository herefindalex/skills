# Company & Role Investigator

Understand the company, locate the role, form challenge hypotheses, and prepare interview validation questions. This plugin provides research instructions, evidence rules, and a report template to distinguish facts, limited inferences, alternatives, and unknowns.

Version 0.1.1. The Skills-only package has no MCP server, hooks, publisher-operated backend, or runtime Python dependency.

## Usage

The [Skill entry](publish/company-role-investigator/skills/investigate-company-role/SKILL.md) and its references are under `publish/company-role-investigator/`. Preserve the plugin's relative directory structure when installing. See the [OpenAI plugin documentation](https://developers.openai.com/plugins/deploy/connect-chatgpt) for host setup.

Supply the company name, official website, and job description or URL. For example:

> Investigate the following company and role. Explain the company and product first, then the role's responsibilities, authority, and likely challenges. Include alternatives and neutral interview questions that could test your interpretation. Company: ...; JD: ... . Identify sources and unknowns.

For an update after an interview, provide the relevant passages from prior research and the new information. A company-only request can start with company research; role analysis needs role-specific material. Research responses follow the user's requested language.

## Local checks and packaging

Python 3.11 or later, standard library only. Run from this project directory:

```bash
python3 -m unittest discover -s tests -v
python3 tools/check_package.py --root publish/company-role-investigator --mode release --approved release/approved-files.json
python3 tools/build_package.py --root publish/company-role-investigator --mode release --approved release/approved-files.json --output dist/company-role-investigator-0.1.1.zip
python3 -m zipfile -t dist/company-role-investigator-0.1.1.zip
```

Build only from `publish/company-role-investigator/`. Reviewed file hashes are in `release/approved-files.json`; review changed source files before updating that list. The builder refuses to overwrite an existing archive. Upload the generated ZIP through the OpenAI plugin submission workflow. Directory publication remains subject to platform checks and review.

## Internal material

Private cases, evaluation outputs, execution records, reviews, handoff documents, and release preparation notes are stored under `docs/internal/` and excluded by `.gitignore`. Generated archives are stored under the ignored `dist/` directory. Neither directory is included in the plugin package.

See the [privacy policy](https://herefindalex.github.io/skills/company-role-investigator/privacy-policy/) for data-handling details.

Publisher: Alex Chang. Support: herefindalex@gmail.com. Repository license: [MIT](../LICENSE).
