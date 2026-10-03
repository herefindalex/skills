"""Temporary test fixtures, never distributed inside the plugin."""
from pathlib import Path
import hashlib
import json

SCHEMA = 'https://agent-plugins.org/schemas/1.0.0/plugin.schema.json'
SKILL = 'skills/investigate-company-role/SKILL.md'


def make_package(root: Path) -> Path:
    root.mkdir(parents=True, exist_ok=True)
    (root / 'plugin.json').write_text(json.dumps({
        '$schema': SCHEMA, 'name': 'company-role-investigator',
        'version': '0.1.0', 'description': 'Research company and role evidence.'
    }), encoding='utf-8')
    p = root / SKILL
    p.parent.mkdir(parents=True, exist_ok=True)
    p.write_text('---\nname: investigate-company-role\n'
                 'description: "Use when investigating company and role context."\n'
                 '---\n# Research\nUse actual sources.\n', encoding='utf-8')
    return root


def approve(root: Path) -> dict[str, str]:
    return {p.relative_to(root).as_posix(): hashlib.sha256(p.read_bytes()).hexdigest()
            for p in sorted(root.rglob('*')) if p.is_file() and not p.is_symlink()}


def edit_manifest(root: Path, **changes: object) -> None:
    p = root / 'plugin.json'
    data = json.loads(p.read_text(encoding='utf-8'))
    data.update(changes)
    p.write_text(json.dumps(data), encoding='utf-8')
