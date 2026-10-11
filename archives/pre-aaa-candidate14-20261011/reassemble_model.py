#!/usr/bin/env python3
"""Reassemble and verify the unchanged pre-AAA candidate 14 Blender file."""
from pathlib import Path
import hashlib
import json

root = Path(__file__).resolve().parent
manifest = json.loads((root / 'MODEL_PARTS.json').read_text())
target = root / manifest['file_name']
if target.exists():
    h = hashlib.sha256(target.read_bytes()).hexdigest()
    if target.stat().st_size == manifest['bytes'] and h == manifest['sha256']:
        print('Already present and verified:', target)
        raise SystemExit(0)
    raise SystemExit('Refusing to overwrite a different existing file: ' + str(target))
temporary = target.with_suffix(target.suffix + '.reassembling')
if temporary.exists():
    raise SystemExit('Temporary output already exists; inspect it before retrying: ' + str(temporary))
whole_hash = hashlib.sha256()
total = 0
with temporary.open('xb') as out:
    for part in manifest['parts']:
        path = root / part['path']
        content = path.read_bytes()
        if len(content) != part['bytes'] or hashlib.sha256(content).hexdigest() != part['sha256']:
            raise SystemExit('Part verification failed: ' + part['path'])
        out.write(content)
        whole_hash.update(content)
        total += len(content)
if total != manifest['bytes'] or whole_hash.hexdigest() != manifest['sha256']:
    raise SystemExit('Whole-file verification failed; original output has not been replaced.')
temporary.rename(target)
print('Verified:', target)
print('Bytes:', total)
print('SHA256:', whole_hash.hexdigest())
