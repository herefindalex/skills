#!/usr/bin/env python3
"""Validate this project's skills-only package contract (not an official schema).

No network calls. Hash approval preserves reviewed bytes; it does not prove that
those bytes are truthful, licensed, private-data-free, or accepted by a host.
"""
from __future__ import annotations

import argparse
import hashlib
import json
import os
from pathlib import Path, PurePosixPath
import re
import stat
import sys
from typing import Any
from urllib.parse import unquote, urlsplit

SCHEMA = 'https://agent-plugins.org/schemas/1.0.0/plugin.schema.json'
SLUG = re.compile(r'^[a-z0-9]+(?:-[a-z0-9]+)*$')
SEMVER = re.compile(r'^(0|[1-9]\d*)\.(0|[1-9]\d*)\.(0|[1-9]\d*)(?:-[0-9A-Za-z.-]+)?(?:\+[0-9A-Za-z.-]+)?$')
SHA256 = re.compile(r'^[0-9a-f]{64}$')
FORBIDDEN_KEYS = {'apps', 'hooks', 'mcpservers', 'mcp', 'skills'}
ROOT_KEYS = {'$schema','name','version','description','extensions','author','homepage','repository','license','keywords'}
INTERFACE_KEYS = {'displayName','shortDescription','longDescription','developerName','category','capabilities','websiteURL','privacyPolicyURL','termsOfServiceURL','defaultPrompt','brandColor','composerIcon','logo','screenshots'}
Finding = dict[str, str]


def finding(code: str, path: str, message: str) -> Finding:
    return {'code':code, 'path':path, 'message':message}


def _unique_pairs(pairs: list[tuple[str, Any]]) -> dict[str, Any]:
    result: dict[str, Any] = {}
    for key, value in pairs:
        if key in result:
            raise ValueError(f'duplicate JSON key: {key}')
        result[key] = value
    return result


def load_json_bytes(data: bytes) -> Any:
    return json.loads(data.decode('utf-8'), object_pairs_hook=_unique_pairs)


def _read_regular(path: Path) -> bytes:
    """Read one regular file without following a final symlink where supported."""
    flags = os.O_RDONLY | getattr(os, 'O_NOFOLLOW', 0) | getattr(os, 'O_NONBLOCK', 0)
    fd = os.open(path, flags)
    try:
        if not stat.S_ISREG(os.fstat(fd).st_mode):
            raise ValueError('not a regular file')
        with os.fdopen(fd, 'rb', closefd=False) as handle:
            return handle.read()
    finally:
        os.close(fd)


def read_snapshot(root: Path) -> tuple[dict[str, bytes], list[Finding]]:
    """Snapshot only regular files. Never recurse into symlinks or special files."""
    data: dict[str, bytes] = {}
    errors: list[Finding] = []
    try:
        if not stat.S_ISDIR(root.lstat().st_mode):
            return {}, [finding('NON_REGULAR_FILE','.', 'Root must be a real directory, not a symlink.')]
    except OSError as exc:
        return {}, [finding('NON_REGULAR_FILE','.',str(exc))]

    def visit(directory: Path) -> None:
        try:
            entries = sorted(directory.iterdir())
        except OSError as exc:
            errors.append(finding('NON_REGULAR_FILE',directory.relative_to(root).as_posix(),str(exc)))
            return
        for p in entries:
            rel = p.relative_to(root).as_posix()
            try:
                mode = p.lstat().st_mode
                if stat.S_ISDIR(mode):
                    # Block special component directories even when empty.
                    if any(x.startswith('.') or x in {'hooks','scripts','agents','private-cases','private-evaluations'} for x in PurePosixPath(rel).parts):
                        errors.append(finding('FORBIDDEN_FILE',rel,'Unsupported directory for this skills-only project.'))
                    visit(p)
                elif stat.S_ISREG(mode):
                    data[rel] = _read_regular(p)
                else:
                    errors.append(finding('NON_REGULAR_FILE',rel,'Symlink or special file is not allowed.'))
            except (OSError, ValueError) as exc:
                errors.append(finding('NON_REGULAR_FILE',rel,str(exc)))
    visit(root)
    return data, errors


def _safe_key(key: str) -> bool:
    return (isinstance(key,str) and bool(key) and '\\' not in key and ':' not in key
            and not key.startswith('/') and all(p not in {'','..','.'} for p in key.split('/')))


def _allowed_file(rel: str) -> bool:
    p = PurePosixPath(rel)
    if rel == 'plugin.json':
        return True
    if any(part.startswith('.') for part in p.parts):
        return False
    if len(p.parts) == 2 and p.parts[0] == 'assets':
        return p.suffix.lower() == '.png'
    if len(p.parts) >= 3 and p.parts[0] == 'skills' and SLUG.fullmatch(p.parts[1]):
        return p.suffix == '.md' and not any(x in {'hooks','scripts','agents'} for x in p.parts[2:])
    return False


def _forbidden_keys(obj: Any, path: str = 'plugin.json') -> list[Finding]:
    errors: list[Finding] = []
    if isinstance(obj, dict):
        for key, value in obj.items():
            if key.lower() in FORBIDDEN_KEYS:
                errors.append(finding('FORBIDDEN_FILE',path,f'Forbidden configuration key: {key}'))
            errors.extend(_forbidden_keys(value,path))
    elif isinstance(obj, list):
        for value in obj:
            errors.extend(_forbidden_keys(value,path))
    return errors


def _link_error(root: Path, origin: str, target: str, files: dict[str, bytes]) -> Finding | None:
    target = target.strip().strip('<>')
    # Do not allow network-path or Windows paths to masquerade as relative links.
    if not target or target.startswith('#'):
        return None
    if target.startswith('/') or '\\' in target:
        return finding('PATH_ESCAPE',origin,f'Unsafe reference: {target}')
    try:
        parsed = urlsplit(target)
    except ValueError as exc:
        return finding("PATH_ESCAPE", origin, f"Malformed reference: {exc}")
    if parsed.scheme:
        if parsed.scheme.lower() in {'https','http','mailto'}:
            return None
        return finding('PATH_ESCAPE',origin,f'Unsupported reference scheme: {target}')
    decoded = unquote(parsed.path)
    if not decoded:
        return None
    if decoded.startswith('/') or '\\' in decoded or ':' in decoded or '\x00' in decoded:
        return finding('PATH_ESCAPE',origin,f'Unsafe reference: {target}')
    base = root.resolve()
    candidate = (base / PurePosixPath(origin).parent / decoded).resolve()
    if not candidate.is_relative_to(base):
        return finding('PATH_ESCAPE',origin,f'Reference leaves package root: {target}')
    key = candidate.relative_to(base).as_posix()
    if key not in files and not any(k.startswith(key.rstrip('/')+'/') for k in files):
        return finding('MISSING_REFERENCE',origin,f'Missing local reference: {target}')
    return None


def _markdown_targets(text: str) -> list[str]:
    # This project uses inline links and reference definitions, not arbitrary HTML.
    text = re.sub(r'^```[^\n]*\n.*?^```\s*$', '', text, flags=re.M|re.S)
    inline = re.findall(r'!?\[[^\]\n]*\]\(\s*(<[^>\n]+>|[^\s)]+)',text)
    definitions = re.findall(r'^\s*\[[^\]\n]+\]:\s*(<[^>\n]+>|\S+)',text,flags=re.M)
    return inline+definitions


def _skill_errors(rel: str, text: str) -> list[Finding]:
    errors: list[Finding] = []
    lines = text.splitlines()
    try:
        if not lines or lines[0] != '---':
            raise ValueError('Missing front matter.')
        end = lines.index('---',1)
        if len('\n'.join(lines[1:end])) > 1024:
            raise ValueError('Front matter exceeds project limit of 1024 characters.')
        fields: dict[str,str] = {}
        for line in lines[1:end]:
            key, sep, value = line.partition(':')
            if not sep or key not in {'name','description'} or key in fields:
                raise ValueError('Use exactly name and description, each on one line.')
            value = value.strip()
            if value.startswith('"'):
                value = json.loads(value)
            elif value.startswith("'"):
                if not value.endswith("'"):
                    raise ValueError('Unclosed single quote.')
                value = value[1:-1].replace("''", "'")
            elif (value.startswith(('[', '{', '|', '>', '&', '*', '!', '@', '%'))
                  or ': ' in value or ' #' in value
                  or value.lower() in {'null','true','false','yes','no','on','off','~','.nan','.inf'}
                  or re.fullmatch(r'[-+]?\d+(?:\.\d+)?',value)):
                raise ValueError('Use an ordinary text scalar or a JSON-quoted string, not YAML collections/types.')
            if not isinstance(value,str) or not value.strip() or value in {'|','>'}:
                raise ValueError('Front matter values must be nonempty one-line strings.')
            fields[key] = value
        if set(fields) != {'name','description'}:
            raise ValueError('Missing required front matter field.')
        if fields['name'] != PurePosixPath(rel).parts[1] or not SLUG.fullmatch(fields['name']):
            raise ValueError('Skill name must be the kebab-case directory name.')
        if not '\n'.join(lines[end+1:]).strip():
            raise ValueError('Missing instruction body.')
    except (ValueError, TypeError) as exc:
        errors.append(finding('MANIFEST_SHAPE',rel,str(exc)))
    return errors


def validate_snapshot(root: Path, files: dict[str, bytes], *, mode: str,
                      approved: dict[str,str] | None = None) -> list[Finding]:
    if mode not in {'draft','release'}:
        raise ValueError('mode must be draft or release')
    errors: list[Finding] = []
    for rel in files:
        if not _safe_key(rel):
            errors.append(finding('PATH_ESCAPE',rel,'Invalid package-relative path.'))
        if not _allowed_file(rel):
            errors.append(finding('FORBIDDEN_FILE',rel,'File outside the project distribution layout.'))

    manifest: dict[str, Any] = {}
    try:
        obj = load_json_bytes(files.get('plugin.json',b''))
        if not isinstance(obj,dict):
            raise ValueError('Manifest must be an object.')
        manifest = obj
        errors.extend(_forbidden_keys(manifest))
        if set(manifest)-ROOT_KEYS:
            raise ValueError('Unsupported top-level manifest keys.')
        if manifest.get('$schema') != SCHEMA:
            raise ValueError('Expected portable Agent Plugins schema.')
        if not isinstance(manifest.get('name'),str) or not SLUG.fullmatch(manifest['name']):
            raise ValueError('Invalid kebab-case name.')
        if not isinstance(manifest.get('version'),str) or not SEMVER.fullmatch(manifest['version']):
            raise ValueError('Expected semantic version.')
        if not isinstance(manifest.get('description'),str) or not manifest['description'].strip():
            raise ValueError('Missing description.')
        extensions = manifest.get('extensions',{})
        if not isinstance(extensions,dict) or set(extensions)-{'com.openai'}:
            raise ValueError('Only the com.openai extension is supported by this project.')
        openai = extensions.get('com.openai',{})
        if not isinstance(openai,dict) or set(openai)-{'interface'}:
            raise ValueError('Only interface metadata is allowed in the OpenAI extension.')
        interface = openai.get('interface',{})
        if not isinstance(interface,dict) or set(interface)-INTERFACE_KEYS:
            raise ValueError('Invalid interface metadata shape.')
    except (ValueError, TypeError) as exc:
        errors.append(finding('MANIFEST_SHAPE','plugin.json',str(exc)))
        interface = {}

    skill_paths = [rel for rel in files if re.fullmatch(r'skills/[^/]+/SKILL\.md',rel)]
    if not skill_paths:
        errors.append(finding('MISSING_REFERENCE','skills/','No discoverable SKILL.md found.'))
    for rel, data in files.items():
        if rel.endswith('.md'):
            try:
                text = data.decode('utf-8')
            except UnicodeError:
                errors.append(finding('MANIFEST_SHAPE',rel,'Markdown must be UTF-8.'))
                continue
            if rel in skill_paths:
                errors.extend(_skill_errors(rel,text))
            for target in _markdown_targets(text):
                error = _link_error(root,rel,target,files)
                if error:
                    errors.append(error)

    image_refs: list[tuple[str, Any]] = [(k, interface[k]) for k in ['logo','composerIcon'] if k in interface]
    if 'screenshots' in interface:
        shots = interface['screenshots']
        if not isinstance(shots, list):
            errors.append(finding('RELEASE_METADATA','plugin.json','screenshots must be a list of local asset paths.'))
        else:
            image_refs.extend((f'screenshots[{i}]', value) for i, value in enumerate(shots))
    for key, value in image_refs:
        if not isinstance(value,str) or not value.startswith('./assets/'):
            errors.append(finding('RELEASE_METADATA','plugin.json',f'{key} must be a local ./assets/ path.'))
        else:
            error = _link_error(root,'plugin.json',value,files)
            if error:errors.append(error)

    if mode == 'release':
        for key in ['displayName','shortDescription','longDescription','developerName','category','logo','composerIcon','privacyPolicyURL']:
            if not isinstance(interface.get(key),str) or not interface[key].strip():
                errors.append(finding('RELEASE_METADATA','plugin.json',f'Missing release metadata: {key}'))
        prompts = interface.get('defaultPrompt')
        if not isinstance(prompts,list) or not prompts or not all(isinstance(x,str) and x.strip() for x in prompts):
            errors.append(finding('RELEASE_METADATA','plugin.json','Missing nonempty starter prompts.'))
        if approved is None:
            errors.append(finding('UNAPPROVED_CONTENT','.', 'Release requires reviewed SHA-256 approval.'))

    if approved is not None:
        if not isinstance(approved,dict):
            errors.append(finding('UNAPPROVED_CONTENT','.', 'Approval must be a path-to-SHA256 object.'))
        else:
            for rel,digest in approved.items():
                if not isinstance(rel,str) or not _safe_key(rel):
                    errors.append(finding('PATH_ESCAPE',str(rel),'Invalid approval path.'))
                if not isinstance(digest,str) or not SHA256.fullmatch(digest):
                    errors.append(finding('UNAPPROVED_CONTENT',str(rel),'Invalid SHA-256 value.'))
            for rel in sorted(set(files)^set(approved)):
                errors.append(finding('UNAPPROVED_CONTENT',rel,'Package and approved file sets differ.'))
            for rel in set(files)&set(approved):
                if hashlib.sha256(files[rel]).hexdigest() != approved[rel]:
                    errors.append(finding('UNAPPROVED_CONTENT',rel,'Bytes differ from reviewed content.'))
    # Stable, deduplicated diagnostics, useful for tests and review logs.
    return [dict(zip(('code','path','message'),row)) for row in sorted({(e['code'],e['path'],e['message']) for e in errors})]


def validate_package(root: Path, *, mode: str,
                     approved: dict[str,str] | None = None) -> list[Finding]:
    if mode not in {'draft','release'}:
        raise ValueError('mode must be draft or release')
    root = Path(root)
    files, errors = read_snapshot(root)
    return errors + validate_snapshot(root,files,mode=mode,approved=approved)


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--root',required=True,type=Path)
    parser.add_argument('--mode',choices=['draft','release'],default='draft')
    parser.add_argument('--approved',type=Path)
    args = parser.parse_args()
    try:
        approved = load_json_bytes(args.approved.read_bytes()) if args.approved else None
        errors = validate_package(args.root,mode=args.mode,approved=approved)
    except (OSError,ValueError) as exc:
        print(json.dumps({'ok':False,'error':str(exc)},ensure_ascii=False))
        return 2
    print(json.dumps({'ok':not errors,'findings':errors},ensure_ascii=False,indent=2))
    return 2 if errors else 0

if __name__ == '__main__':
    sys.exit(main())
