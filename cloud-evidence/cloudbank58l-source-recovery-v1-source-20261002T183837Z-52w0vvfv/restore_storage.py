#!/usr/bin/env python3
"""Restore exact archived runtime JSON; never regenerate or overwrite evidence."""
import argparse, gzip, hashlib, json
from pathlib import Path
HERE=Path(__file__).resolve().parent
def digest(b):return hashlib.sha256(b).hexdigest()
def need(ok,message):
    if not ok:raise ValueError(message)
def child(root,relative):
    p=Path(relative);need(not p.is_absolute() and '..' not in p.parts,'Unsafe relative path')
    out=root/p;need(out.resolve().is_relative_to(root.resolve()),'Outside destination')
    return out
def main():
    ap=argparse.ArgumentParser();ap.add_argument('--out',type=Path);ap.add_argument('--verify-only',action='store_true');a=ap.parse_args()
    target=(a.out or HERE).resolve();meta=json.loads((HERE/'storage.json').read_text());cache={};result=[]
    for row in meta['raw_files']:
        key=row['sha256']
        if key not in cache:
            parts=[]
            for part in row['parts']:
                b=child(HERE,part['path']).read_bytes();need(len(b)==part['bytes'] and digest(b)==part['sha256'],'Part identity');parts.append(b)
            z=b''.join(parts);need(len(z)==row['compressed_bytes'] and digest(z)==row['compressed_sha256'],'Compressed identity')
            b=gzip.decompress(z);need(len(b)==row['bytes'] and digest(b)==key,'Full original raw identity');cache[key]=b
        b=cache[key];need(len(b)==row['bytes'],'Alias size');out=child(target,row['path'])
        if out.exists():need(out.is_file() and out.read_bytes()==b,'Existing evidence differs; never overwrite');state='existing_exact'
        elif a.verify_only:state='reconstruction_verified_not_written'
        else:
            out.parent.mkdir(parents=True,exist_ok=True)
            with out.open('xb') as f:f.write(b)
            need(out.read_bytes()==b,'Written evidence identity');state='restored_exact'
        result.append({'path':row['path'],'bytes':len(b),'sha256':key,'state':state})
    print(json.dumps({'verified':True,'raw_paths':len(result),'unique_streams':len(cache),'files':result},indent=2))
if __name__=='__main__':main()
