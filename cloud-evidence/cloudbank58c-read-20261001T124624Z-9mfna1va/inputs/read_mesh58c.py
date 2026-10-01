"""Read existingraw Cunion; comparecoarse15 topology and exportexactrealtriangles."""
import hashlib,json,sys,time
from pathlib import Path
import bpy,numpy as np
P=Path(__file__).resolve().parent;R=P.parent/'recovery-01';sys.path.insert(0,str(R))
from native_geometry58c import geometry,mesh_data
source=R/'cloud_bank58c_union.blend';before=hashlib.sha256(source.read_bytes()).hexdigest();bpy.ops.wm.open_mainfile(filepath=str(source))
print('Readexistingrawunion; computeindependentcoarse15topology',flush=True)
coarse=bpy.data.objects['EDIT58C_coarse15_union'];report,v,ids,tri,tree=geometry(coarse);np.savez_compressed(P/'coarse15-actual-triangles58c.npz',vertices=v,indices=ids)
print('Coarse15component/genus',report['component_count'],[c['genus'] for c in report['components']],flush=True)
bank=bpy.data.objects['CloudBank58C_four_root_density_and_folds'];v,ids,tri=mesh_data(bank);np.savez_compressed(P/'full57-actual-triangles58c.npz',vertices=v,indices=ids)
(P/'coarse15-geometry58c.json').write_text(json.dumps(report,indent=2)+'\n');after=hashlib.sha256(source.read_bytes()).hexdigest();assert before==after
(P/'readback58c.json').write_text(json.dumps(dict(passed=True,source_sha256=before,source_unchanged=before==after,coarse15_component_count=report['component_count'],coarse15_genus=[c['genus'] for c in report['components']],coarse15_geometry_passed=report['closed_geometry_passed'],coarse15_triangles=report['triangles'],full57_triangles=len(ids),world_loaded=False,rendered=False,visual_acceptance=False),indent=2)+'\n')
