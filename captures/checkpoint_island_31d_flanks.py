from pathlib import Path
import json,hashlib
R=Path(__file__).resolve().parents[1]
reports=['reviews/round-31d-rear-flank-independent.md','reviews/round-31d-rear-flank-independent.json']
sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
p=R/'reviews/round-31d-root-evidence.json';d=json.loads(p.read_text())
assert not any(x['path'] in reports for x in d['reports'])
d['reports'] += [dict(path=x,sha256=sha(R/x)) for x in reports]
d['root_findings'] += ['All six independently checked actual source faces avoid current occupied footprints, but shared-vertex one-rings435 and408 intersect actual tree disks. Do not freely drag shared vertices just because sampled face is clear.',
                      'Faces1973/2181 are independently confirmed on actual third operand supporting planes. Face1507 has nearly zero XY projection but8.035m2 real area; it is visible near-vertical wall, not absent surface.']
p.write_text(json.dumps(d,ensure_ascii=False,indent=2),encoding='utf-8')
p=R/'reviews/reference-view-1342-progress-31d.json';d=json.loads(p.read_text());d['evidence']+=reports
d['remaining']+=['For rear source-face remeshing, preserve actual tree-support one-rings or explicitly re-ground changed trees; current2m disks are authoring assumptions. See31d flank independent report.']
p.write_text(json.dumps(d,ensure_ascii=False,indent=2),encoding='utf-8')
note='31d六面有界核验补记：六实际射线与源面全部匹配，六整面均无占用投影；但共享点435一环1107/1108实际碰树盘0.460161/0.008055m²，点408一环24/25/26碰树盘2.533776/5.486331/2.159220m²。不能因命中面无交区就自由拖共享点；沿真实支承边界重划面，或有记录地重贴受影响树。面1973/2181已按整三角的实际凸包支持平面和半空间确认属于第三操作数外壳；1507近竖直，XY投影1.91e-7m²但真实面积8.035m²，不是无面。见 `reviews/round-31d-rear-flank-independent.md/json`。这是下一步原坡联动重塑的边界证据，不是模型或全参考接受。'
with (R/'reviews/round-31c-worklog.md').open('a',encoding='utf-8') as f:f.write('\n\n'+note+'\n')
for name in ['WORKSPACE_RESUME.md','reviews/LOOP.md']:
    p=R/name;s=p.read_text(encoding='utf-8')
    marker='**最新31d原生';pos=s.index('\n',s.index(marker))
    s=s[:pos]+'\n\n'+note+s[pos:]
    p.write_text(s,encoding='utf-8')
print('31d actual shared-vertex and operand provenance findings bound to current checkpoint.')
