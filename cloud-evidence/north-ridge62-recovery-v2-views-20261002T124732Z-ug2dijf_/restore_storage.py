"""Verify canonical compressed stream and literal raw-byte patches; never resurvey."""
from pathlib import Path
import argparse,gzip,hashlib,json,lzma,os
ap=argparse.ArgumentParser();ap.add_argument('--restore-missing',action='store_true');a=ap.parse_args();here=Path(__file__).resolve().parent;root=here.parents[1];m=json.loads((here/'storage.json').read_text())
def sha(b):return hashlib.sha256(b).hexdigest()
def take(p,size,digest):
 b=p.read_bytes()
 if len(b)!=size or sha(b)!=digest:raise ValueError('Stored identity mismatch')
 return b
def keep(row,data):
 if len(data)!=row['bytes'] or sha(data)!=row['sha256']:raise ValueError('Raw identity mismatch')
 name=Path(row['raw'])
 if name.is_absolute() or '..' in name.parts:raise ValueError('Unsafe output')
 p=here/name
 if p.exists():
  if p.is_symlink() or p.read_bytes()!=data:raise ValueError('Different existing raw; never overwrite')
 elif a.restore_missing:
  p.parent.mkdir(parents=True,exist_ok=True)
  with p.open('xb') as f:f.write(data);f.flush();os.fsync(f.fileno())
 print(row['raw'],len(data),row['sha256'],'verified')
for row in m['lossless_gzip']:keep(row,gzip.decompress(take(here/row['stored'],row['stored_bytes'],row['stored_sha256'])))
s=json.loads((root/m['base_manifest']).read_text());entry=next(x for x in s['files'] if x['restore_path']==m['base_entry']);z=b''.join(take(root/p['path'],p['bytes'],p['sha256'])for p in entry['parts'])
if len(z)!=entry['compressed_bytes'] or sha(z)!=entry['compressed_sha256']:raise ValueError('Compressed stream mismatch')
base=lzma.decompress(z)
if len(base)!=entry['bytes'] or sha(base)!=m['base_raw_sha256'] or sha(base)!=entry['sha256']:raise ValueError('Base raw mismatch')
for row in m['exact_raw_splices']:
 n=row['offset'];old=row['expected_ascii'].encode('ascii');new=row['replacement_ascii'].encode('ascii')
 if base[n:n+len(old)]!=old:raise ValueError('Patch preimage mismatch')
 keep(row,base[:n]+new+base[n+len(old):])
