"""Complete, verified local migration. Existing project/history files are never edited."""
from pathlib import Path
import os, sys, json, sqlite3, hashlib, shutil, zipfile, datetime, re, collections, importlib.metadata, site, traceback

ROOT=Path('D:/test6')
BASE=Path('C:/Users/wubugui/.codex')
MAIN='01a06f81-bc4b-7db2-a58f-8cf029138711'
DEST=ROOT/'MIGRATION_20260906'
ARCH=Path(os.environ.get('AETHER_MIGRATION_ARCHIVE_DIR',str(DEST/'archives')))
HISTORY=DEST/'history'
STATE=ARCH/'progress.json'
BUFF=4*1024*1024
CONTROL={'MIGRATION_20260906/FILE_MANIFEST.jsonl','MIGRATION_20260906/PACKAGE_INFO.json'}

def utc():return datetime.datetime.now(datetime.timezone.utc).isoformat()
def norm(p):
    s=str(p).replace('\\','/')
    if s.startswith('//?/'):s=s[4:]
    return s.rstrip('/').lower()
def actual(p):
    s=str(p)
    if s.startswith('\\\\?\\'):s=s[4:]
    return Path(s)
def log(message,**kwargs):
    row={'utc':utc(),'message':message,**kwargs}
    ARCH.mkdir(parents=True,exist_ok=True)
    STATE.write_text(json.dumps(row,ensure_ascii=False,indent=2),encoding='utf8')
    with (ARCH/'migration.log').open('a',encoding='utf8') as f:f.write(json.dumps(row,ensure_ascii=False)+'\n')
    print(json.dumps(row,ensure_ascii=False),flush=True)
def sha(path):
    h=hashlib.sha256()
    with path.open('rb') as f:
        for data in iter(lambda:f.read(BUFF),b''):h.update(data)
    return h.hexdigest()
def ro(name):
    c=sqlite3.connect((BASE/name).as_uri()+'?mode=ro',uri=True)
    c.row_factory=sqlite3.Row
    return c
def write_json(path,data):path.write_text(json.dumps(data,ensure_ascii=False,indent=2),encoding='utf8')
def walk_files(folder):
    failures=[]
    def failed(e):failures.append(str(e))
    for parent,ds,fs in os.walk(folder,onerror=failed):
        for d in ds:
            p=Path(parent)/d
            if p.is_symlink():raise RuntimeError('Unresolved directory link '+str(p))
        for name in fs:
            p=Path(parent)/name
            if p.is_symlink():raise RuntimeError('Unresolved file link '+str(p))
            yield p
    if failures:raise RuntimeError(str(failures))

def export_history():
    HISTORY.mkdir(parents=True,exist_ok=False)
    state=ro('state_5.sqlite')
    all_rows=[dict(r) for r in state.execute('SELECT * FROM threads')]
    ids={r['id'] for r in all_rows if norm(r['cwd'])==norm(ROOT)}|{MAIN}
    edges=[dict(r) for r in state.execute('SELECT * FROM thread_spawn_edges')]
    changed=True
    while changed:
        before=set(ids)
        for edge in edges:
            if edge['parent_thread_id'] in ids:ids.add(edge['child_thread_id'])
        ids|={r['id'] for r in all_rows if any(i in r.get('source','') for i in ids)}
        changed=before!=ids
    selected=[r for r in all_rows if r['id'] in ids]
    source_paths={actual(r['rollout_path']) for r in selected}
    # Scan session metadata as well as the index, including archived/orphan records.
    scanned=0
    for folder in [BASE/'sessions',BASE/'archived_sessions']:
        for p in folder.rglob('*.jsonl'):
            scanned+=1
            with p.open('r',encoding='utf8') as f:
                first=f.readline()
            try:meta=json.loads(first).get('payload',{})
            except json.JSONDecodeError:continue
            if meta.get('id') in ids or norm(meta.get('cwd',''))==norm(ROOT):
                source_paths.add(p)
                if meta.get('id'):ids.add(meta['id'])
    assert any(MAIN in p.name for p in source_paths)
    raw=HISTORY/'raw'; readable=HISTORY/'readable'
    raw.mkdir();readable.mkdir()
    summary=[];clip_names=set();external_media=set()
    resource_pattern=re.compile(r"""(?i)[A-Z]:[\\/][^<>"\r\n|]*?\.(?:png|jpg|jpeg|webp|gif|mp4|wav|glb|blend|gltf|svg)(?=$|[\s"'<>),\]])""")
    def strings(value):
        if isinstance(value,str):yield value
        elif isinstance(value,list):
            for x in value:yield from strings(x)
        elif isinstance(value,dict):
            for x in value.values():yield from strings(x)
    for src in sorted(source_paths,key=str):
        assert src.is_file(),src
        n=src.stat().st_size
        with src.open('rb') as f:data=f.read(n)
        assert len(data)==n
        dest=raw/src.name;dest.write_bytes(data)
        # Keep a byte-for-byte snapshot. An in-flight partial final record is
        # retained verbatim and explicitly recorded rather than silently dropped.
        good=bad=messages=0;last_timestamp=None
        thread_id=src.stem[-36:]
        with (readable/(thread_id+'.md')).open('w',encoding='utf8') as out:
            out.write('# 本地对话记录导出\n\n原始完整记录见 ../raw/'+src.name+'\n\n')
            for line_number,line in enumerate(data.splitlines(),1):
                try:event=json.loads(line)
                except json.JSONDecodeError:
                    bad+=1;continue
                good+=1;last_timestamp=event.get('timestamp',last_timestamp)
                payload=event.get('payload',{});kind=event.get('type')
                if kind=='event_msg' and payload.get('type') in ['user_message','agent_message']:
                    role='用户' if payload['type']=='user_message' else '助手'
                    text=payload.get('message','')
                    if not isinstance(text,str):text=json.dumps(text,ensure_ascii=False)
                    out.write('\n## '+role+' · '+str(event.get('timestamp',''))+'\n\n'+text+'\n')
                    messages+=1
                elif kind=='response_item' and payload.get('type') in ['function_call','function_call_output','custom_tool_call','custom_tool_call_output']:
                    out.write('\n<details><summary>工具记录 · '+str(event.get('timestamp',''))+'</summary>\n\n')
                    out.write('~~~~json\n'+json.dumps(payload,ensure_ascii=False,indent=2)+'\n~~~~\n\n</details>\n')
                for text in strings(payload):
                    clip_names.update(re.findall(r'codex-clipboard-[0-9a-fA-F-]+\.(?:png|jpe?g|webp)',text,re.I))
                    for match in resource_pattern.findall(text):
                        candidate=actual(match)
                        try:
                            if len(str(candidate))<1500 and candidate.is_file() and not norm(candidate).startswith(norm(ROOT)+'/'):
                                external_media.add(candidate)
                        except OSError:pass
        summary.append({'source':str(src),'snapshot':'history/raw/'+src.name,'thread_id':thread_id,'bytes':n,
                        'sha256':hashlib.sha256(data).hexdigest(),'valid_json_records':good,
                        'partial_or_invalid_records_preserved':bad,'visible_messages':messages,
                        'last_record_timestamp':last_timestamp,'snapshot_utc':utc()})
        log('History snapshot saved',thread_id=thread_id,bytes=n,records=good)
    metadata=HISTORY/'metadata';metadata.mkdir()
    database_reports=[]
    # Filtered SQLite copies retain all columns and exact stored values for the
    # selected tasks; unrelated account credentials and other projects are not copied.
    for name in ['state_5.sqlite','thread_history_1.sqlite','goals_1.sqlite','queue_1.sqlite']:
        src=ro(name);dst=sqlite3.connect(metadata/name)
        tables=src.execute("SELECT name,sql FROM sqlite_master WHERE type='table' AND name NOT LIKE 'sqlite_%'").fetchall()
        report={}
        for table,sql in tables:
            dst.execute(sql)
            columns=[r[1] for r in src.execute('PRAGMA table_info("'+table+'")')]
            if table=='_sqlx_migrations':rows=list(src.execute('SELECT * FROM "'+table+'"'))
            elif 'thread_id' in columns:
                rows=list(src.execute('SELECT * FROM "'+table+'" WHERE thread_id IN ('+','.join('?'*len(ids))+')',tuple(ids)))
            elif table=='threads':
                rows=list(src.execute('SELECT * FROM threads WHERE id IN ('+','.join('?'*len(ids))+')',tuple(ids)))
            elif table=='thread_spawn_edges':
                rows=[r for r in src.execute('SELECT * FROM thread_spawn_edges') if r['parent_thread_id'] in ids or r['child_thread_id'] in ids]
            else:
                rows=[r for r in src.execute('SELECT * FROM "'+table+'"') if any(isinstance(v,str) and any(i in v for i in ids) for v in r)]
            if rows:dst.executemany('INSERT INTO "'+table+'" VALUES ('+','.join('?'*len(columns))+')',[tuple(r) for r in rows])
            report[table]=len(rows)
        dst.commit()
        integrity=dst.execute('PRAGMA integrity_check').fetchone()[0];assert integrity=='ok'
        dst.close();src.close();database_reports.append({'database':name,'rows':report,'integrity_check':integrity})
    state.close()
    index=BASE/'session_index.jsonl'
    if index.exists():
        with index.open('r',encoding='utf8') as src,(metadata/'session_index.jsonl').open('w',encoding='utf8') as dst:
            for line in src:
                if any(i in line for i in ids):dst.write(line)
    write_json(metadata/'threads.json',selected)
    write_json(metadata/'spawn_edges.json',[e for e in edges if e['parent_thread_id'] in ids or e['child_thread_id'] in ids])
    goal=ro('goals_1.sqlite')
    write_json(DEST/'GOAL_SNAPSHOT.json',[dict(r) for r in goal.execute('SELECT * FROM thread_goals WHERE thread_id=?',(MAIN,))])
    goal.close()
    attachments=DEST/'attachments';attachments.mkdir()
    copied=[];missing=[]
    for name in sorted(clip_names):
        candidates=[Path('C:/Users/wubugui/AppData/Local/Temp')/name]+list((BASE/'attachments').rglob(name))
        existing=next((p for p in candidates if p.is_file()),None)
        if existing:external_media.add(existing)
        else:missing.append(name)
    for p in sorted(external_media,key=str):
        target=attachments/(hashlib.sha256(str(p).encode()).hexdigest()[:12]+'-'+p.name)
        shutil.copy2(p,target)
        copied.append({'source':str(p),'path':target.relative_to(DEST).as_posix(),'sha256':sha(target),'bytes':target.stat().st_size})
    # The original task reference is mandatory and checked against the source game copy.
    reference=ROOT/'assets/reference.jpg'
    assert sha(reference)=='7785b260a60fa66a03dec3fa53b4d83c3e9f29df0448388bdf8dfb1ac6c2cb53'
    write_json(HISTORY/'HISTORY_INDEX.json',{'main_thread_id':MAIN,'included_thread_ids':sorted(ids),'metadata_files_scanned':scanned,
        'scope':'All local session and archived-session records for this project directory plus descendant tasks, including exact raw bytes and filtered history/goal databases.',
        'snapshots':summary,'databases':database_reports,'external_media_copied':copied,
        'clipboard_names_not_found_on_disk':missing,'original_reference_sha256':sha(reference),
        'snapshot_cutoff_utc':utc(),'later_packaging_messages':'Packaging after this cutoff is recorded in archives/migration.log and the migration handoff.'})
    log('History export complete',threads=len(ids),rollouts=len(summary),external_media=len(copied),missing_clipboards=missing)

def prepare():
    assert not (DEST/'PREPARED.json').exists(),'Already prepared; use build, not prepare.'
    DEST.mkdir(exist_ok=True);ARCH.mkdir(exist_ok=True)
    (DEST/'.gdignore').write_text('',encoding='utf8')
    export_history()
    external=[]
    python=Path('C:/Users/wubugui/AppData/Local/Programs/Python/Python310')
    user_site=Path('C:/Users/wubugui/AppData/Roaming/Python/Python310/site-packages')
    for source,target in [(python,'external/python/Python310'),(user_site,'external/python/user_site')]:
        assert source.is_dir(),source
        external.append({'source':str(source),'target':target})
    for p in Path('C:/Users/wubugui/AppData/Roaming/Godot/app_userdata').iterdir():
        if p.is_dir() and p.name.startswith('Aether'):
            external.append({'source':str(p),'target':'external/godot_userdata/'+p.name})
    viz=BASE/'visualizations/2026/09/05'/MAIN
    if viz.is_dir():external.append({'source':str(viz),'target':'external/visualizations/'+MAIN})
    packages={}
    for name in ['numpy','scipy','opencv-python','pillow','shapely']:
        try:packages[name]=importlib.metadata.version(name)
        except importlib.metadata.PackageNotFoundError:packages[name]='not found under this distribution name'
    write_json(DEST/'EXTERNAL_SOURCES.json',external)
    write_json(DEST/'RUNTIME_ENVIRONMENT.json',{'python':sys.version,'python_source':str(python),
        'user_site_source':str(user_site),'packages':packages,'godot':'4.5.1 stable Windows x64',
        'blender':'4.5.0 Windows x64','original_project_root':str(ROOT),'original_os':'Windows',
        'gpu_at_last_render':'NVIDIA GeForce RTX 4070 SUPER; OpenGL Compatibility',
        'scope':'Complete installed Python310 tree and complete user-level site-packages are embedded in the ZIP, not only a package list. Blender and Godot binaries are already in .tools.'})
    write_json(DEST/'PREPARED.json',{'utc':utc(),'main_thread_id':MAIN,'status':'Project development frozen for migration; visual goal remains unfinished and paused.'})
    log('Migration sources prepared',external_sources=len(external),packages=packages)

def sources():
    values=[];seen=set();dirs=set()
    for p in walk_files(ROOT):
        rel=p.relative_to(ROOT).as_posix()
        if rel.startswith('MIGRATION_20260906/archives/') or rel in CONTROL:continue
        values.append((p,'test6/'+rel,'project'))
    for entry in json.loads((DEST/'EXTERNAL_SOURCES.json').read_text(encoding='utf8')):
        source=Path(entry['source'])
        for p in walk_files(source):
            values.append((p,'test6/MIGRATION_20260906/'+entry['target']+'/'+p.relative_to(source).as_posix(),'external'))
    for parent, subdirs, files in os.walk(ROOT):
        rel=Path(parent).relative_to(ROOT).as_posix()
        if rel=='MIGRATION_20260906/archives' or rel.startswith('MIGRATION_20260906/archives/'):continue
        dirs.add('test6/' if rel=='.' else 'test6/'+rel+'/')
    for entry in json.loads((DEST/'EXTERNAL_SOURCES.json').read_text(encoding='utf8')):
        source=Path(entry['source'])
        for parent, subdirs, files in os.walk(source):
            rel=Path(parent).relative_to(source).as_posix()
            dirs.add('test6/MIGRATION_20260906/'+entry['target']+('/' if rel=='.' else '/'+rel+'/'))
    for p,name,kind in values:
        key=name.lower()
        assert key not in seen,'Archive path collision '+name
        seen.add(key)
        for parent in Path(name).parents:
            if str(parent)!='.':dirs.add(parent.as_posix()+'/')
    return values,sorted(dirs)

def build():
    assert (DEST/'HANDOFF.md').is_file() and (DEST/'START_HERE.md').is_file()
    values,dirs=sources()
    before={name:(p.stat().st_size,p.stat().st_mtime_ns) for p,name,_ in values}
    total=sum(size for size,stamp in before.values())
    target=ARCH/'Aether_Full_Migration_20260906.zip'
    assert not target.exists()
    free=shutil.disk_usage(ARCH).free
    assert free>total*1.08+300_000_000,(free,total)
    log('Archive started',input_files=len(values),uncompressed_bytes=total,free_bytes=free)
    records=[];done=0
    with zipfile.ZipFile(target,'x',compression=zipfile.ZIP_DEFLATED,compresslevel=1,allowZip64=True,strict_timestamps=False) as z:
        for d in dirs:z.writestr(d,b'')
        for i,(p,name,kind) in enumerate(values):
            info=zipfile.ZipInfo.from_file(p,arcname=name,strict_timestamps=False)
            info.compress_type=zipfile.ZIP_STORED if p.suffix.lower() in ['.zip','.png','.jpg','.jpeg','.webp','.mp4','.7z','.gz'] else zipfile.ZIP_DEFLATED
            info._compresslevel=1
            h=hashlib.sha256();n=0
            with p.open('rb') as src,z.open(info,'w',force_zip64=True) as dst:
                for data in iter(lambda:src.read(BUFF),b''):
                    h.update(data);dst.write(data);n+=len(data)
            after=(p.stat().st_size,p.stat().st_mtime_ns)
            assert before[name]==after and n==after[0],'Source changed while archiving '+str(p)
            records.append({'path':name,'source':str(p),'kind':kind,'bytes':n,'mtime_ns':after[1],'sha256':h.hexdigest()})
            done+=n
            if i%2000==0:log('Archiving files',completed=i+1,total=len(values),bytes=done)
        manifest=b''.join((json.dumps(r,ensure_ascii=False)+'\n').encode('utf8') for r in records)
        (ARCH/'FILE_MANIFEST.jsonl').write_bytes(manifest)
        z.writestr('test6/MIGRATION_20260906/FILE_MANIFEST.jsonl',manifest)
        info={'created_utc':utc(),'root':'test6','main_thread_id':MAIN,'files':len(records),'directories':len(dirs),
              'source_bytes':total,'project_files':sum(r['kind']=='project' for r in records),
              'external_files':sum(r['kind']=='external' for r in records),'history_cutoff':json.loads((HISTORY/'HISTORY_INDEX.json').read_text(encoding='utf8'))['snapshot_cutoff_utc'],
              'manifest_sha256':hashlib.sha256(manifest).hexdigest(),
              'scope':'Every file in the frozen project directory, hidden folders and historical artifacts included, plus all exported local task histories, original available referenced media, Python runtime/user packages and Aether user data.',
              'self_exclusions':['Only archives/ output and live packaging log are excluded to avoid recursive inclusion. FILE_MANIFEST.jsonl and PACKAGE_INFO.json are added as control entries.'],
              'game_goal_complete':False,'game_goal_status':'paused for computer migration'}
        info_bytes=json.dumps(info,ensure_ascii=False,indent=2).encode('utf8')
        (ARCH/'PACKAGE_INFO.json').write_bytes(info_bytes);z.writestr('test6/MIGRATION_20260906/PACKAGE_INFO.json',info_bytes)
    current={name:(p.stat().st_size,p.stat().st_mtime_ns) for p,name,_ in sources()[0]}
    assert current==before,'Input directory changed during package build'
    log('ZIP written; verifying every archived file',zip_bytes=target.stat().st_size,files=len(records))
    verify(target)

def verify(target=None):
    target=target or ARCH/'Aether_Full_Migration_20260906.zip'
    expected=[json.loads(line) for line in (ARCH/'FILE_MANIFEST.jsonl').read_text(encoding='utf8').splitlines()]
    controls=['test6/MIGRATION_20260906/FILE_MANIFEST.jsonl','test6/MIGRATION_20260906/PACKAGE_INFO.json']
    with zipfile.ZipFile(target,'r') as z:
        entries=[i for i in z.infolist() if not i.is_dir()]
        assert len({i.filename for i in entries})==len(entries)
        assert {i.filename for i in entries}=={r['path'] for r in expected}|set(controls)
        for i,r in enumerate(expected):
            h=hashlib.sha256();n=0
            with z.open(r['path']) as f:
                for data in iter(lambda:f.read(BUFF),b''):h.update(data);n+=len(data)
            assert n==r['bytes'] and h.hexdigest()==r['sha256'],'Archive mismatch '+r['path']
            if i%4000==0:log('Verifying archived SHA256',completed=i+1,total=len(expected))
        for name in controls:
            assert z.read(name)==(ARCH/Path(name).name).read_bytes()
    digest=sha(target)
    (ARCH/'SHA256SUMS.txt').write_text(digest+'  '+target.name+'\n',encoding='ascii')
    report={'passed':True,'completed_utc':utc(),'archive':target.name,'archive_bytes':target.stat().st_size,
        'archive_sha256':digest,'verified_source_files':len(expected),'control_files':len(controls),
        'missing_entries':0,'extra_entries':0,'duplicate_entries':0,'content_hash_mismatches':0,
        'verification':'Every archive member streamed back, ZIP CRC checked by decompressor, SHA256 compared with the original bytes; source path inventory and size/mtime rechecked after build.'}
    write_json(ARCH/'VERIFY_RESULT.json',report)
    log('COMPLETE',**report)

if __name__=='__main__':
    try:
        command=sys.argv[1]
        if command=='prepare':prepare()
        elif command=='build':build()
        elif command=='verify':verify()
        else:raise ValueError(command)
    except Exception:
        ARCH.mkdir(parents=True,exist_ok=True)
        text=traceback.format_exc();(ARCH/'FAILED.txt').write_text(text,encoding='utf8');log('FAILED',error=text)
        raise

