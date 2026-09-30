"""Read-only local inventory for a complete project/thread migration."""
from pathlib import Path
import os, sys, json, shutil, sqlite3, importlib.util
root=Path('D:/test6'); counts={}; total=0; links=[]; errors=[]
for parent, dirs, files in os.walk(root):
    for name in dirs+files:
        p=Path(parent)/name
        if p.is_symlink() or (hasattr(p,'is_junction') and p.is_junction()):links.append(str(p))
    for name in files:
        p=Path(parent)/name
        try:n=p.stat().st_size
        except OSError as e:errors.append([str(p),str(e)]);continue
        key=p.relative_to(root).parts[0]; item=counts.setdefault(key,[0,0]);item[0]+=1;item[1]+=n;total+=n
print(json.dumps({'project':counts,'total_bytes':total,'disk_free':shutil.disk_usage(root).free,'links':links,'errors':errors,'python':sys.executable,'prefix':sys.prefix,'base_prefix':sys.base_prefix},ensure_ascii=False),flush=True)
base=Path('C:/Users/wubugui/.codex')
for name in ['state_5.sqlite','thread_history_1.sqlite','goals_1.sqlite','queue_1.sqlite']:
    p=base/name
    if not p.exists():continue
    try:
        con=sqlite3.connect(p.as_uri()+'?mode=ro',uri=True)
        tables=con.execute("SELECT name FROM sqlite_master WHERE type='table'").fetchall()
        print(name,tables,flush=True)
        for (table,) in tables:
            if any(s in table for s in ['thread','goal','history','session']):print(table,con.execute('PRAGMA table_info("'+table+'")').fetchall(),flush=True)
        con.close()
    except Exception as e:print(type(e).__name__,str(e),flush=True)
for name in ['numpy','scipy','cv2','PIL','shapely']:
    spec=importlib.util.find_spec(name);print('PYDEP',name,spec.origin if spec else None,flush=True)
