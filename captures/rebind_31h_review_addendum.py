from pathlib import Path
import json,hashlib
R=Path(__file__).resolve().parents[1];p=R/'reviews/round-31h-root-evidence.json';d=json.loads(p.read_text(encoding='utf-8'));changed=[]
allowed={'reviews/round-31h-island-independent-review.md','reviews/round-31h-island-independent-review.json'}
for a in d['reports']:
 h=hashlib.sha256((R/a['path']).read_bytes()).hexdigest()
 if h!=a['sha256']:
  assert a['path'] in allowed,a['path']
  changed.append(dict(path=a['path'],previous_sha256=a['sha256'],sha256=h));a['sha256']=h
assert changed
d.setdefault('report_binding_addenda',[]).append(dict(reason='Independent31h reviewer appended exact31i control one-ring localization after root checkpoint. Update only those review-document hashes; native/GPU identities and outcomes unchanged. No runtime rerun.',changes=changed))
p.write_text(json.dumps(d,ensure_ascii=False,indent=2),encoding='utf-8');print(json.dumps(changed,indent=2))
