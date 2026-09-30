from pathlib import Path
import sqlite3,json,os,sys,importlib.util
base=Path('C:/Users/wubugui/.codex'); con=sqlite3.connect((base/'state_5.sqlite').as_uri()+'?mode=ro',uri=True);con.row_factory=sqlite3.Row
rows=[dict(r) for r in con.execute('select id,rollout_path,cwd,source,agent_path,title from threads') if str(r['cwd']).replace('\\','/').lower().rstrip('/')=='d:/test6']
print('PROJECT_THREADS',json.dumps(rows,ensure_ascii=False),flush=True)
ids={r['id'] for r in rows}
print('SPAWN_EDGES',json.dumps([dict(r) for r in con.execute('select * from thread_spawn_edges') if r['parent_thread_id'] in ids],ensure_ascii=False),flush=True)
for folder in [Path(sys.prefix),base/'attachments',base/'visualizations/2026/09/05/01a06f81-bc4b-7db2-a58f-8cf029138711']:
 count=size=0
 for parent,dirs,files in os.walk(folder):
  for name in files:
   p=Path(parent)/name;count+=1;size+=p.stat().st_size
 print('FOLDER',str(folder),count,size,flush=True)
for name in ['numpy','scipy','cv2','PIL','shapely']:
 spec=importlib.util.find_spec(name);print('PYDEP',name,spec.origin if spec else None,flush=True)
for row in rows[:2]:
 p=Path(row['rollout_path'])
 if p.exists():
  with p.open('r',encoding='utf8') as f:first=json.loads(f.readline())
  payload=first.get('payload',{})
  print('META_KEYS',str(p),list(payload),flush=True)
  print('META_SOURCE',payload.get('source'),payload.get('cwd'),payload.get('id'),flush=True)
