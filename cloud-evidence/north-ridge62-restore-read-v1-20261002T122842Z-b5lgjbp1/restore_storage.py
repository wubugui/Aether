"""Verify exact evidence streams and optionally restore missing original files."""
from pathlib import Path
import argparse,gzip,hashlib,json,lzma,os
p=argparse.ArgumentParser();p.add_argument('--restore-missing',action='store_true');a=p.parse_args();here=Path(__file__).resolve().parent;root=here.parents[1];m=json.loads((here/'storage.json').read_text())
def sha(b):return hashlib.sha256(b).hexdigest()
def take(path,size,digest):
 b=path.read_bytes()
 if len(b)!=size or sha(b)!=digest:raise ValueError('Stored size/SHA mismatch: '+str(path))
 return b
def keep(name,b,size,digest):
 if len(b)!=size or sha(b)!=digest:raise ValueError('Original size/SHA mismatch')
 p=Path(name)
 if p.is_absolute() or '..' in p.parts:raise ValueError('Unsafe path')
 dest=here/p
 if dest.exists():
  if dest.is_symlink() or dest.read_bytes()!=b:raise ValueError('Existing raw differs; refusing overwrite')
 elif a.restore_missing:
  dest.parent.mkdir(parents=True,exist_ok=True)
  with dest.open('xb') as f:f.write(b);f.flush();os.fsync(f.fileno())
 print(name,size,digest,'verified')
for r in m['lossless_gzip']:keep(r['raw'],gzip.decompress(take(here/r['stored'],r['stored_bytes'],r['stored_sha256'])),r['bytes'],r['sha256'])
r=m['exact_existing_stream_alias'];source=json.loads((root/r['source_manifest']).read_text());entry=next(x for x in source['files'] if x['restore_path']==r['source_entry']);z=b''.join(take(root/x['path'],x['bytes'],x['sha256']) for x in entry['parts'])
if len(z)!=entry['compressed_bytes'] or sha(z)!=entry['compressed_sha256']:raise ValueError('Concatenated stream differs')
keep(r['raw'],lzma.decompress(z),r['bytes'],r['sha256'])
