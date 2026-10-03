#!/usr/bin/env python3
"""Restore exact original runtime JSON bytes; never recompute or overwrite evidence."""
import argparse,gzip,hashlib,json
from pathlib import Path
HERE=Path(__file__).resolve().parent
def digest(b):return hashlib.sha256(b).hexdigest()
def need(ok,message):
    if not ok:raise ValueError(message)
def child(root,relative):
    p=Path(relative);need(not p.is_absolute() and '..' not in p.parts,'Unsafe relative path');out=root/p
    need(out.resolve().is_relative_to(root.resolve()),'Outside destination');return out
def main():
    ap=argparse.ArgumentParser();ap.add_argument('--out',type=Path);ap.add_argument('--verify-only',action='store_true');a=ap.parse_args()
    target=(a.out or HERE).resolve();meta=json.loads((HERE/'storage.json').read_text());cache={};visiting=set()
    def recover(key):
        if key in cache:return cache[key]
        need(key not in visiting,'Storage dependency cycle');visiting.add(key);row=meta['objects'][key];need(row['sha256']==key,'Object key identity')
        if row['codec']=='gzip-mtime0':
            chunks=[]
            for part in row['parts']:
                b=child(HERE,part['path']).read_bytes();need(len(b)==part['bytes'] and digest(b)==part['sha256'],'Part identity');chunks.append(b)
            z=b''.join(chunks);need(len(z)==row['compressed_bytes'] and digest(z)==row['compressed_sha256'],'Compressed identity');b=gzip.decompress(z)
        elif row['codec']=='literal-byte-splice-v1':
            b=recover(row['base_sha256']);last_end=0
            for edit in row['changes']:
                at=edit['offset'];before=bytes.fromhex(edit['delete_hex']);need(type(at) is int and at>=last_end and at+len(before)<=len(b),'Ordered nonoverlapping byte splice');need(b[at:at+len(before)]==before,'Original literal bytes');last_end=at+len(before)
            for edit in reversed(row['changes']):
                at=edit['offset'];before=bytes.fromhex(edit['delete_hex']);b=b[:at]+bytes.fromhex(edit['insert_hex'])+b[at+len(before):]
        else:raise ValueError('Unknown exact storage codec')
        need(len(b)==row['bytes'] and digest(b)==key,'Full original byte identity');cache[key]=b;visiting.remove(key);return b
    result=[]
    for row in meta['files']:
        b=recover(row['sha256']);need(len(b)==row['bytes'],'Alias size');out=child(target,row['path'])
        if out.exists():need(out.is_file() and out.read_bytes()==b,'Existing evidence differs; never overwrite');state='existing_exact'
        elif a.verify_only:state='reconstruction_verified_not_written'
        else:
            out.parent.mkdir(parents=True,exist_ok=True)
            with out.open('xb') as f:f.write(b)
            need(out.read_bytes()==b,'Written byte identity');state='restored_exact'
        result.append(dict(path=row['path'],bytes=len(b),sha256=row['sha256'],state=state))
    print(json.dumps(dict(verified=True,raw_paths=len(result),unique_objects=len(cache),files=result),indent=2))
if __name__=='__main__':main()
