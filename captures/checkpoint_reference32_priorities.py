from pathlib import Path
import json,hashlib
R=Path(__file__).resolve().parents[1]
note='**下一步按固定参考总图推进32轮：先前景A，再右岸层次，再海面光色。** 独立直接对31i夜/昼主图与ref1342，确认前景A的大平草台、被遮住的岩崖和塔/两屋/树群关系是第一项主要场景差距；其次右岸岩岬/低湾/后山与港村纵深，第三为密集横向水光和暖灯层次。C/D31i保留为未接受候选，其背图仅为结构诊断，不能以无原图的隐藏面假精度无限阻塞主视图和全部20参考。请从 `captures/lantern_islands_study_20l/island_a.blend` 做独立新版本的精细原生前景地形，先核实际建筑/树/路与参考投影，不重跑旧整套生成器或覆盖生产。原生路径和实际世界锚点见 `reviews/round-32-source-pointers.md`；独立优先级 `reviews/round-32-reference-priorities.md/json`。尚无32新模型；31i全部原生/GPU/审查已结束。完整20参考及原开场Goal保持active，未减少场景或天气范围。'
for name in ['WORKSPACE_RESUME.md','reviews/LOOP.md']:
 p=R/name;s=p.read_text(encoding='utf-8');assert '**下一步按固定参考总图推进32轮' not in s
 first,rest=s.split('\n',1);p.write_text(first+'\n\n'+note+'\n'+rest,encoding='utf-8')
for name in ['REFERENCE_SCENES.md','WORLD_SCENE_PLAN.md']:
 p=R/name;s=p.read_text(encoding='utf-8');assert '**下一步按固定参考总图推进32轮' not in s
 p.write_text(s+'\n\n'+note+'\n',encoding='utf-8')
p=R/'reviews/round-31i-root-evidence.json';d=json.loads(p.read_text(encoding='utf-8'));assert 'next_main_reference_priority' not in d
paths=['reviews/round-32-reference-priorities.md','reviews/round-32-reference-priorities.json','reviews/round-32-source-pointers.md']
d['next_main_reference_priority']=dict(order=['ForegroundA native proportions/cliff visibility/building-tree layout','Right shoreline headlands, low coves, inland hills and harbor depth','Water specular pattern and warm-light response'],rationale='Direct main-reference review. No-reference C/D rear diagnostics are bounded structure checks and must not replace primary framing or all20-scene scope.',evidence=[dict(path=s,sha256=hashlib.sha256((R/s).read_bytes()).hexdigest()) for s in paths],new32_model_exists=False)
p.write_text(json.dumps(d,ensure_ascii=False,indent=2),encoding='utf-8')
print('Verified main-reference priorities and native source pointers saved; whole goal active.')
