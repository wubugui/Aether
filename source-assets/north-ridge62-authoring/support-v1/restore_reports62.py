#!/usr/bin/env python3
"""Restore only absent raw report bytes, never overwrite any existing file."""
from pathlib import Path
import gzip,hashlib,json
D=Path(__file__).resolve().parent
manifest=json.loads((D/'storage.json').read_text())
for name,record in manifest['reports'].items():
 if name not in {'support-results.json','attempt02-rejected-unaffected-piece-policy.json'}:raise ValueError('Unexpected restore target')
 packed=D/(name+'.gz');raw=packed.read_bytes()
 if len(raw)!=record['gzip']['bytes']or hashlib.sha256(raw).hexdigest()!=record['gzip']['sha256']:raise ValueError('Gzip identity mismatch '+name)
 value=gzip.decompress(raw)
 if len(value)!=record['raw']['bytes']or hashlib.sha256(value).hexdigest()!=record['raw']['sha256']:raise ValueError('Raw identity mismatch '+name)
 target=D/name
 if target.exists():
  if target.read_bytes()!=value:raise ValueError('Existing differing report; refused to overwrite '+name)
 else:
  with target.open('xb')as f:f.write(value)
 print('Verified identical raw report',name)
