from pathlib import Path
root=Path(__file__).resolve().parents[1]
for name in ['harbor_assembly','harbor_path_runtime']:
    source=(root/('captures/'+name+'_22f.gd')).read_text(encoding='utf-8').replace('22f','22g')
    source=source.replace('Vector3(3.90,0.02,3.5)','Vector3(3.90,0.02,4.4)').replace('Vector3(0,0,-3.1)','Vector3(0,0,-4.0)')
    target=root/('captures/'+name+'_22g.gd');assert not target.exists();target.write_text(source,encoding='utf-8')
source=(root/'tools/render_harbor_assembly_22f.py').read_text(encoding='utf-8')
source=source.replace("run=ValidationRun(root,'harbor-assembly-22f'","run=ValidationRun(root,'harbor-assembly-22g'")
source=source.replace('harbor_assembly_22f.gd','harbor_assembly_22g.gd').replace('harbor_path_runtime_22f.gd','harbor_path_runtime_22g.gd').replace("p['placement']=='candidate_22f'","p['placement']=='candidate_22g'")
source=source.replace("'--path',root,'--script'","'--path',root,'--audio-driver','Dummy','--script'")
source=source.replace('Temporary, no full reference, movement, seabed or production acceptance.','Boat center moved4.0m seaward relative22a after measured grounding. Visual-only run uses Dummy audio after prior WASAPI device invalidation; actual OpenGL GPU retained. Temporary, no audio, full reference, movement, seabed or production acceptance.')
target=root/'tools/render_harbor_assembly_22g.py';assert not target.exists();target.write_text(source,encoding='utf-8')
