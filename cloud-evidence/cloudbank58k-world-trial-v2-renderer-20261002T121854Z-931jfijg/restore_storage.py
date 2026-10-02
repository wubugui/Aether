"""Verify compressed migration evidence, optionally restore only missing exact raw."""
from pathlib import Path
import argparse,gzip,hashlib,json,os
p=argparse.ArgumentParser();p.add_argument('--restore-missing',action='store_true');args=p.parse_args()
here=Path(__file__).resolve().parent
for row in json.loads((here/'storage.json').read_text())['lossless_gzip']:
 for key in ['raw','stored']:
  if Path(row[key]).name!=row[key]:raise ValueError('Local evidence file only')
 data=(here/row['stored']).read_bytes()
 if len(data)!=row['stored_bytes'] or hashlib.sha256(data).hexdigest()!=row['stored_sha256']:raise ValueError('Stored identity mismatch')
 raw=gzip.decompress(data)
 if len(raw)!=row['bytes'] or hashlib.sha256(raw).hexdigest()!=row['sha256']:raise ValueError('Original identity mismatch')
 dest=here/row['raw']
 if dest.exists():
  if dest.is_symlink() or dest.read_bytes()!=raw:raise ValueError('Different existing raw: refusing overwrite')
 elif args.restore_missing:
  with dest.open('xb') as f:f.write(raw);f.flush();os.fsync(f.fileno())
 print(row['raw'],len(raw),row['sha256'],'verified')
