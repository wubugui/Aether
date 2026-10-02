"""Only verify or restore the exact already-computed NPZ, without resurveying."""
from pathlib import Path
import argparse,hashlib,json,os
p=argparse.ArgumentParser();p.add_argument('--restore-missing',action='store_true');a=p.parse_args();here=Path(__file__).resolve().parent;m=json.loads((here/'CHECKPOINT.json').read_text())['npz_storage'];data=bytearray()
for part in m['parts']:
 if Path(part['name']).name!=part['name']:raise ValueError('Local chunk name required')
 b=(here/part['name']).read_bytes()
 if len(b)!=part['bytes'] or hashlib.sha256(b).hexdigest()!=part['sha256']:raise ValueError('Chunk differs')
 data.extend(b)
if len(data)!=m['bytes'] or hashlib.sha256(data).hexdigest()!=m['sha256']:raise ValueError('Original NPZ differs')
dest=here/m['raw']
if dest.exists():
 if dest.is_symlink() or dest.read_bytes()!=data:raise ValueError('Different existing NPZ; no overwrite')
elif a.restore_missing:
 with dest.open('xb') as f:f.write(data);f.flush();os.fsync(f.fileno())
print(json.dumps({'passed':True,'bytes':len(data),'sha256':m['sha256'],'no_survey_or_engine_executed':True}))
