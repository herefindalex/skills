#!/usr/bin/env python3
"""Build a reproducible ZIP from reviewed bytes; never overwrite an archive.

Requires a filesystem supporting atomic hard-link creation in the output
folder. No installation, publishing, network access, or approval generation.
"""
from __future__ import annotations

import argparse
import hashlib
import json
import os
from pathlib import Path
import sys
import tempfile
import zipfile

if __package__:
    from .check_package import read_snapshot, validate_snapshot, load_json_bytes
else:
    from check_package import read_snapshot, validate_snapshot, load_json_bytes


def build_package(root: Path, output: Path, *, mode: str,
                  approved: dict[str, str]) -> dict[str, str]:
    """Validate and archive the same in-memory bytes using an explicit allowlist."""
    root, output = Path(root), Path(output)
    if mode not in {'draft','release'}:
        raise ValueError('mode must be draft or release')
    if os.path.lexists(output):
        raise FileExistsError(f'Archive already exists: {output}')
    if output.resolve().is_relative_to(root.resolve()):
        raise ValueError('PATH_ESCAPE: output must be outside the plugin root')
    if not isinstance(approved,dict):
        raise ValueError('UNAPPROVED_CONTENT: approval must be a path-to-SHA256 object')
    approved = approved.copy()
    files, errors = read_snapshot(root)
    errors += validate_snapshot(root,files,mode=mode,approved=approved)
    if errors:
        raise ValueError(json.dumps(errors,ensure_ascii=False))

    # Validate_snapshot hashes these immutable byte strings. Do not re-open
    # sources when writing the archive: they might have changed since review.
    output.parent.mkdir(parents=True,exist_ok=True)
    fd, temp_name = tempfile.mkstemp(prefix='.cri-',suffix='.zip.tmp',dir=output.parent)
    os.close(fd)
    temp = Path(temp_name)
    try:
        with zipfile.ZipFile(temp,'w',compression=zipfile.ZIP_DEFLATED,compresslevel=9) as archive:
            for rel in sorted(approved):
                info = zipfile.ZipInfo(rel,date_time=(1980,1,1,0,0,0))
                info.create_system = 3
                info.external_attr = 0o100644 << 16
                info.compress_type = zipfile.ZIP_DEFLATED
                archive.writestr(info,files[rel],compress_type=zipfile.ZIP_DEFLATED,compresslevel=9)
        with temp.open('rb') as handle:
            os.fsync(handle.fileno())
        digest = hashlib.sha256(temp.read_bytes()).hexdigest()
        # Atomic no-replace publish on the same filesystem. A race with another
        # writer fails rather than overwriting their file. Finally removes temp.
        os.link(temp,output)
    finally:
        temp.unlink(missing_ok=True)
    return {'archive':str(output.resolve()),'sha256':digest,'file_count':str(len(files))}


def main() -> int:
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--root',required=True,type=Path)
    parser.add_argument('--output',required=True,type=Path)
    parser.add_argument('--mode',choices=['draft','release'],default='draft')
    parser.add_argument('--approved',required=True,type=Path)
    args=parser.parse_args()
    try:
        approved=load_json_bytes(args.approved.read_bytes())
        result=build_package(args.root,args.output,mode=args.mode,approved=approved)
    except (OSError,ValueError) as exc:
        print(json.dumps({'ok':False,'error':str(exc)},ensure_ascii=False))
        return 2
    print(json.dumps(result,ensure_ascii=False,indent=2))
    return 0

if __name__=='__main__':
    sys.exit(main())
