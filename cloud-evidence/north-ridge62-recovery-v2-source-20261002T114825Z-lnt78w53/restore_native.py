"""Verify canonical Git chunks; explicitly restore exact missing originals only."""
import argparse,hashlib,json,lzma,os
from pathlib import Path
HERE=Path(__file__).resolve().parent
ROOT=HERE.parents[1]
def require(ok,label):
 if not ok:raise ValueError(label)
def digest(data):return hashlib.sha256(data).hexdigest()
def checked_path(root,name):
 p=Path(name);require(not p.is_absolute() and '..' not in p.parts,'Safe repository-relative path required')
 out=root/p;require(not out.is_symlink(),'Symlink destination forbidden')
 require(out.resolve().is_relative_to(root.resolve()),'Resolved path escaped root');return out
def main():
 ap=argparse.ArgumentParser();ap.add_argument('--restore-missing',action='store_true');ap.add_argument('--destination-root',type=Path);args=ap.parse_args()
 require(args.destination_root is None or args.restore_missing,'Destination requires explicit restore')
 target=(args.destination_root or ROOT).resolve();data=json.loads((HERE/'native-storage.json').read_text());rows=[]
 for item in data['files']:
  encoded=bytearray()
  for part in item['parts']:
   b=checked_path(ROOT,part['path']).read_bytes();require(len(b)==part['bytes'] and digest(b)==part['sha256'],'Chunk size/SHA mismatch');encoded.extend(b)
  require(len(encoded)==item['compressed_bytes'] and digest(encoded)==item['compressed_sha256'],'Compressed stream size/SHA mismatch')
  raw=lzma.decompress(encoded);require(len(raw)==item['bytes'] and digest(raw)==item['sha256'],'Restored original size/SHA mismatch')
  path=checked_path(target,item['restore_path']);status='verified_chunks_only'
  if path.exists():require(path.is_file() and path.stat().st_size==len(raw) and digest(path.read_bytes())==item['sha256'],'Different existing original: never overwrite');status='existing_exact'
  elif args.restore_missing:
   path.parent.mkdir(parents=True,exist_ok=True)
   with path.open('xb') as f:f.write(raw);f.flush();os.fsync(f.fileno())
   require(path.stat().st_size==len(raw) and digest(path.read_bytes())==item['sha256'],'Written original mismatch');status='restored_exact'
  rows.append(dict(path=item['restore_path'],bytes=len(raw),sha256=item['sha256'],status=status))
 print(json.dumps(dict(passed=True,destination=str(target),files=rows,native_open_performed=False),indent=2))
if __name__=='__main__':main()
