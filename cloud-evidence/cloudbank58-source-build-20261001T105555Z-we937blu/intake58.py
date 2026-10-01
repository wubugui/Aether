"""Read exact saved native anchors and old GLB triangles without starting an app."""
import hashlib, json, re, struct
from pathlib import Path
import numpy as np

P=Path(__file__).resolve().parent
ROOT=P.parents[1]
PROJECT=ROOT/'candidates/round40-exclusive-20260930/project'
SCENE=PROJECT/'scenes/candidate52f/Game52f.tscn'
PINNED_SCENE='201f667747406b1414a298a6b5433ac1550d8b447dff8f6cb6823d94d2acbd7c'
RUN=ROOT/'cloud-evidence/cloudsea52h-d-ab-front-20261001T102736Z-svczz9fo'
SELECTED={'CloudSea_0_0','CloudSea_0_1','CloudSea_1_0','CloudSea_1_1'}
sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()


def glb_reader():
    def read(path):
        raw=path.read_bytes();size,kind=struct.unpack_from('<II',raw,12);assert kind==0x4e4f534a
        data=json.loads(raw[20:20+size]);start=20+size
        length,kind=struct.unpack_from('<II',raw,start);assert kind==0x004e4942
        binary=raw[start+8:start+8+length]
        def accessor(index):
            a=data['accessors'][index];view=data['bufferViews'][a['bufferView']]
            dtype={5126:'<f4',5125:'<u4',5123:'<u2',5121:'u1'}[a['componentType']]
            dim={'SCALAR':1,'VEC2':2,'VEC3':3,'VEC4':4}[a['type']];item=np.dtype(dtype).itemsize
            offset=view.get('byteOffset',0)+a.get('byteOffset',0)
            return np.ndarray((a['count'],dim),dtype=dtype,buffer=binary,offset=offset,strides=(view.get('byteStride',dim*item),item)).copy()
        meshes=[]
        for node in data['nodes']:
            if 'mesh' not in node:continue
            assert not any(k in node for k in ('matrix','rotation','translation','scale','children')),'Unexpected GLB transform; stop rather than guess'
            for primitive in data['meshes'][node['mesh']]['primitives']:
                positions=accessor(primitive['attributes']['POSITION']).astype(np.float64)
                indices=accessor(primitive['indices']).reshape(-1,3)
                meshes.append(dict(name=node['name'],triangles=positions[indices]))
        return meshes
    return read


def native_intake():
    assert sha(SCENE)==PINNED_SCENE,'The authoritative saved52f source changed; stop and review.'
    text=SCENE.read_text();reader=glb_reader()
    build=json.loads((RUN/'build-report-52f.json').read_text())
    proof=json.loads((RUN/'verified-saved-52f.json').read_text())
    assert proof['saved_native_audit_passed'] and proof['candidate_sha256']==PINNED_SCENE
    inventory={r['root'].split('/')[-1]:r for r in build['inventory']}
    assets={};files=[]
    for vi in range(3):
        paths=[ROOT/f'source-assets/cloud-sea52e/cloud_sea_52e_{vi}.glb',
               ROOT/f'source-assets/cloud-sea52f/variants/cloud_sea_52f_additions_{vi}.glb']
        assets[vi]=sum((reader(p) for p in paths),[])
        for path in paths:
            copy=PROJECT/f'assets/clouds{"52e" if "cloud-sea52e" in str(path) else "52f"}/{path.name}'
            assert sha(copy)==sha(path),'Source GLB differs from the verified native copy.'
            files.append(dict(path=str(path.relative_to(ROOT)),sha256=sha(path),bytes=path.stat().st_size))
    roots=[];world=[]
    pattern=r'\[node name="(CloudSea_[^"]+)" type="Node3D" parent="SkyRegion39"\]\ntransform = Transform3D\(([^)]+)\)'
    for match in re.finditer(pattern,text):
        values=np.array([float(x) for x in match[2].split(',')]);basis=values[:9].reshape(3,3).T;position=values[9:]
        inv=inventory[match[1]];variant=inv['variant'];parts=[]
        assert len(assets[variant])==5
        for part in assets[variant]:
            tri=part['triangles']@basis.T+position
            parts.append(dict(name=part['name'],triangles=len(tri),bounds=[tri.reshape(-1,3).min(0).tolist(),tri.reshape(-1,3).max(0).tolist()]))
            world.append(dict(root=match[1],name=part['name'],triangles=tri,selected=match[1] in SELECTED))
        pts=np.concatenate([m['triangles'].reshape(-1,3) for m in world[-5:]])
        roots.append(dict(name=match[1],variant=variant,basis_columns=values[:9].tolist(),basis_rows=basis.tolist(),position=position.tolist(),
                          selected=match[1] in SELECTED,bounds=[pts.min(0).tolist(),pts.max(0).tolist()],parts=parts))
    assert len(roots)==25 and sum(r['selected'] for r in roots)==4
    def block(name,parent):
        m=re.search(r'\[node name="'+re.escape(name)+r'"[^\n]*parent="'+re.escape(parent)+r'"[^\n]*\]\n(.*?)(?=\n\[node|\Z)',text,re.S)
        assert m;return m[0]
    sea=block('Ocean','World');world_node=block('World','.');sky=block('SkyRegion39','.')
    assert 'transform =' not in sea and 'transform =' not in world_node and 'transform =' not in sky
    sea_mesh=re.search(r'mesh = SubResource\("([^"]+)"\)',sea)[1]
    sea_resource=re.search(r'\[sub_resource type="PlaneMesh" id="'+re.escape(sea_mesh)+r'"\]\n(.*?)(?=\n\[)',text,re.S)[0]
    assert 'orientation =' not in sea_resource  # default PlaneMesh faces +Y at Y=0
    report=json.loads((RUN/'images/report.json').read_text())
    camera=report['captures'][0]['camera_transform']
    return dict(status='Read-only saved native52f intake; no new runtime or preview',source_scene=str(SCENE.relative_to(ROOT)),source_scene_sha256=sha(SCENE),
                source_glbs=files,roots=roots,camera_transform=camera,camera_fov=report['captures'][0]['camera_fov'],
                ocean=dict(saved_world_y=0.,basis='Identity World and Ocean native transforms plus native horizontal PlaneMesh; actual gameplay waves are not assessed',node=sea,mesh=sea_resource),
                selected_mesh_count=20,unselected_mesh_count=105,visual_acceptance=False),world


if __name__=='__main__':
    report,_=native_intake()
    (P/'native-intake58.json').write_text(json.dumps(report,indent=2)+'\n')
    print(json.dumps({'selected':[r for r in report['roots'] if r['selected']], 'ocean':report['ocean'],'scene_sha256':report['source_scene_sha256']},indent=2))
