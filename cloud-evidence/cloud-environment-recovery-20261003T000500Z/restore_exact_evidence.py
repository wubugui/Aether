"""One-shot recovery audit. Does not import project code or launch any engine.

Only the reviewed pure-storage scripts are invoked. Other historical manifests
are decoded as literal gzip/XZ bytes, never reserialized or recreated.
"""
from pathlib import Path
import gzip, hashlib, json, lzma, os, subprocess, sys

ROOT = Path('/workspace/scratch/a29d03198654/Aether').resolve()
OUT = Path(__file__).resolve().parent
def sha(data): return hashlib.sha256(data).hexdigest()
def require(ok, message):
    if not ok: raise ValueError(message)
def child(base, relative):
    p = Path(relative)
    require(not p.is_absolute() and '..' not in p.parts, 'Unsafe relative path')
    dest = base / p
    require(not dest.is_symlink() and dest.resolve().is_relative_to(ROOT), 'Escaping/symlink path')
    return dest
def exact(path, size, digest):
    b = path.read_bytes()
    require(len(b) == size and sha(b) == digest, 'Identity mismatch: ' + str(path))
    return b
def rel(path): return str(path.relative_to(ROOT))
def command(args):
    return subprocess.run(args, cwd=ROOT, env={**os.environ, 'PYTHONDONTWRITEBYTECODE':'1', 'GIT_OPTIONAL_LOCKS':'0'}, capture_output=True, text=True)
def ignored(path): return command(['git','check-ignore','--quiet','--',rel(path)]).returncode == 0
tracked=set(command(['git','ls-files']).stdout.splitlines())
groups=[]
def row(base, name, size, digest, **other):
    return dict(path=child(base,name), bytes=size, sha256=digest, **other)
def basic(base, x):
    if 'raw_path' in x:
        raw=x['raw_path']; size=x['raw_bytes']; digest=x['raw_sha256']
    elif 'original_path' in x:
        raw=x['original_path']; size=x['original_bytes']; digest=x['original_sha256']
    elif 'original' in x:
        raw=x['original']; size=x['original_bytes']; digest=x['original_sha256']
    else:
        raw=x['raw']; size=x['bytes']; digest=x['sha256']
    if 'xz_path' in x: encoded=x['xz_path']; esize=x['xz_bytes']; esha=x['xz_sha256']; codec='xz'
    elif 'gzip_path' in x: encoded=x['gzip_path']; esize=x['gzip_bytes']; esha=x['gzip_sha256']; codec='gzip'
    else:
        encoded=x.get('lossless_storage',x.get('stored_path',x.get('stored')))
        esize=x.get('stored_bytes',x.get('gzip_bytes')); esha=x.get('stored_sha256',x.get('gzip_sha256')); codec='gzip'
    require(encoded is not None and esize is not None and esha is not None,'Unknown simple storage schema')
    return row(base,raw,size,digest,stored=child(base,encoded),stored_bytes=esize,stored_sha256=esha,codec=codec)

reviewed_storage={
 '633a757bf7e9065595ac8ca3b8dd814cc673a1ee208e552113f04055d34feb99':[],
 '586368c3c2af7b93722d336c6a41e374a606154c2987e2b35bcf8661416dd207':[],
 '0f1b98f1b5b8240dfeb1e0d51ff3aad921e24916c4c6d704a531b3503a808cc9':['--restore-missing'],
 'b731e899947652136d0b245fb18bb6c83b0e84f1e4677dba965ecfc99dc6f453':['--restore-missing'],
 'fe1faf8e34626bb011dd9f603ca5cfd82bcc040cb55a62c45a50e7e4daef0b18':['--restore-missing'],
}
for manifest in sorted(ROOT.rglob('*storage*.json')):
    if manifest.relative_to(ROOT).parts[0]=='delivery': continue # Inventory, not a recovery contract.
    meta=json.loads(manifest.read_text()); base=manifest.parent; rows=[]; script=None; args=[]
    if manifest.name=='native-storage.json':
        script=base/'restore_native.py'; args=['--restore-missing']
        require(sha(script.read_bytes())=='fab4155f6a2fb0265d07814107a2bbeebe8f0093444a36347bd6e83e311e7f89','Native restorer changed')
        rows=[row(ROOT,x['restore_path'],x['bytes'],x['sha256']) for x in meta['files']]
    elif (base/'restore_storage.py').exists() and manifest.name=='storage.json':
        script=base/'restore_storage.py'; digest=sha(script.read_bytes())
        require(digest in reviewed_storage,'Unreviewed storage script'); args=reviewed_storage[digest]
        entries=meta.get('raw_files',meta.get('files',[]))
        rows=[row(base,x['path'],x['bytes'],x['sha256']) for x in entries]
        rows += [row(base,x['raw'],x['bytes'],x['sha256']) for x in meta.get('lossless_gzip',[])]
        rows += [row(base,x['raw'],x['bytes'],x['sha256']) for x in meta.get('exact_raw_splices',[])]
        if 'exact_existing_stream_alias' in meta:
            x=meta['exact_existing_stream_alias']; rows.append(row(base,x['raw'],x['bytes'],x['sha256']))
    elif isinstance(meta,dict) and 'reports' in meta:
        # The reviewed support restorer is equivalently literal gzip; use it unchanged.
        script=base/'restore_reports62.py'
        rows=[row(base,k,v['raw']['bytes'],v['raw']['sha256']) for k,v in meta['reports'].items()]
    else:
        if isinstance(meta,list): entries=meta
        elif 'lossless_gzip' in meta: entries=meta['lossless_gzip']
        elif 'files' in meta: entries=meta['files']
        else: entries=[meta]
        rows=[basic(base,x) for x in entries]
    require(rows, 'Empty restore manifest '+str(manifest))
    groups.append(dict(manifest=manifest,script=script,args=args,rows=rows))

base=ROOT/'cloud-evidence/cloudbank-next-footprint-checkpoint-20261002'
meta=json.loads((base/'CHECKPOINT.json').read_text())['npz_storage']
groups.append(dict(manifest=base/'CHECKPOINT.json',script=base/'restore_grid.py',args=['--restore-missing'],rows=[row(base,meta['raw'],meta['bytes'],meta['sha256'])]))

records=[]; issues=[]; runs=[]
for i,g in enumerate(groups):
    label=rel(g['manifest']); before={}
    try:
        for r in g['rows']:
            p=r['path']; before[rel(p)]=p.exists()
            if p.exists(): exact(p,r['bytes'],r['sha256'])
            else:
                require(rel(p) not in tracked, 'Missing tracked file cannot be silently restored: '+rel(p))
                require(ignored(p),'Missing target not ignored: '+rel(p))
        if g['script']:
            script=g['script']; result=command([sys.executable,'-B',str(script),*g['args']])
            (OUT/f'restore-run-{i:02d}.stdout').write_text(result.stdout)
            (OUT/f'restore-run-{i:02d}.stderr').write_text(result.stderr)
            runs.append(dict(script=rel(script),script_sha256=sha(script.read_bytes()),arguments=g['args'],returncode=result.returncode))
            require(result.returncode==0,'Restorer returned '+str(result.returncode))
        else:
            for r in g['rows']:
                packed=exact(r['stored'],r['stored_bytes'],r['stored_sha256'])
                b=(gzip.decompress if r['codec']=='gzip' else lzma.decompress)(packed)
                require(len(b)==r['bytes'] and sha(b)==r['sha256'],'Decoded original identity mismatch')
                p=r['path']
                if p.exists(): require(p.read_bytes()==b,'Existing original differs')
                else:
                    p.parent.mkdir(parents=True,exist_ok=True)
                    with p.open('xb') as f: f.write(b); f.flush(); os.fsync(f.fileno())
        for r in g['rows']:
            b=exact(r['path'],r['bytes'],r['sha256'])
            is_json=r['path'].suffix=='.json'
            if is_json:json.loads(b)
            records.append(dict(manifest=label,path=rel(r['path']),bytes=len(b),sha256=r['sha256'],state='existing_exact' if before[rel(r['path'])] else 'restored_exact',ignored=ignored(r['path']),json_parsed=is_json))
        print('VERIFIED',label,len(g['rows']),sum(x['bytes'] for x in g['rows']),flush=True)
    except Exception as exc:
        issues.append(dict(manifest=label,error=str(exc))); print('BLOCKED',label,exc,flush=True)
    (OUT/'restoration-results.json').write_text(json.dumps(dict(files=records,issues=issues,scripts=runs),indent=2)+'\n')
summary=dict(recovered_paths=sum(r['state']=='restored_exact' for r in records),recovered_bytes=sum(r['bytes'] for r in records if r['state']=='restored_exact'),verified_paths=len(records),verified_bytes=sum(r['bytes'] for r in records),issue_count=len(issues),tracked_status=command(['git','status','--porcelain=v1','-uno']).stdout,untracked_status=command(['git','ls-files','--others','--exclude-standard']).stdout)
(OUT/'restoration-summary.json').write_text(json.dumps(summary,indent=2)+'\n')
print(json.dumps(summary,indent=2))
