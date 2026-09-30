from pathlib import Path
R=Path(__file__).resolve().parents[1];p=R/'captures/checkpoint_island_31i.py';assert not p.exists()
s=(R/'captures/checkpoint_island_31g.py').read_text(encoding='utf-8').replace('31g','31i')
s=s.replace('reference-view-1342-progress-31f.json','reference-view-1342-progress-31h.json')
s=s.replace('full-depth-independent.json','shared-edge-intake.json')
s=s.replace('31f actual native source, rear sector cut and448 faces replaced by84 triangles using8 authored3D controls;637 old internal edges removed,70 boundary edges preserved.','Actual31h source;5 controls moved,4 common-edge points added and2 real finite-width shoulder bands formed by face_split; adjacent faces update together. All final triangles and occupied support independently checked.')
s=s.replace('A/B20l; C/D31i actual rear topology replacement','A/B20l; C/D31i real shoulder tops/front drops and staggered low roots over31h rear shell')
s=s.replace('31i真实拓扑重接接续','31i有限宽肩接续')
p.write_text(s,encoding='utf-8')
