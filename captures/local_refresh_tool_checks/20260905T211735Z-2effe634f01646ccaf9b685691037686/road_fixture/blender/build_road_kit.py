"""Build separate roads from native Godot curves, split on terrain triangles.

Every road polygon is clipped against the actual Blender terrain topology.
Its entire surface follows one terrain triangle, rather than only placing
the four corners of a long quad onto different heights.

First export the existing saved Godot Routes with tools/export_road_routes.gd.
Do not run author_road_routes.gd for a geometry refresh: it reauthors curves.
Then run Blender --background --python blender/build_road_kit.py --
  --road=Trail_Crownreach --road=Trail_HillHamlet
No --road retains the full road-kit build. Selection is checked before writes;
unselected GLB/Blend files and manifest entries are retained. This tool never
writes Godot scenes, Path3D curves, instance transforms, or road_routes.json.
"""
from pathlib import Path
import argparse,copy,json,sys,math,numpy as np
ROOT=Path(__file__).resolve().parents[1]

def parse_args(argv):
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--road',action='append',default=[],help='Exact exported Godot route name; repeat for multiple roads.')
    return parser.parse_args(argv)

def merge_entries(existing,updates):
    by_name={item['name']:item for item in updates}
    result=[copy.deepcopy(by_name.get(item['name'],item)) for item in existing]
    names={item['name'] for item in existing}
    result.extend(copy.deepcopy(item) for item in updates if item['name'] not in names)
    return result

def prepare_build(root,selected):
    # Keep this read-only: even a late misspelled selection must fail before
    # an earlier valid road can overwrite a GLB, Blend, or manifest.
    routes=json.loads((root/'assets/road_routes.json').read_text())
    kit_path=root/'assets/road_kit.json'
    existing=json.loads(kit_path.read_text()) if kit_path.exists() else []
    report_path=root/'captures/road-authoring-validation.json'
    reports=json.loads(report_path.read_text()) if report_path.exists() else []
    for label,items in [('native routes',routes),('road kit',existing),('road reports',reports)]:
        if not isinstance(items,list) or any(not isinstance(item,dict) or not isinstance(item.get('name'),str) for item in items):
            raise ValueError('Invalid '+label)
        names=[item['name'] for item in items]
        if len(set(names))!=len(names):raise ValueError('Duplicate names in '+label)
    names={route['name'] for route in routes}
    unknown=set(selected)-names
    if unknown:raise ValueError('Unknown native Godot road(s): '+', '.join(sorted(unknown)))
    chosen=[route for route in routes if not selected or route['name'] in selected]
    old={item['name']:item for item in existing}
    entries=[]
    for route in chosen:
        name=route['name']
        if not name or any(c not in 'abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789_-' for c in name):
            raise ValueError('Unsupported road asset name: '+name)
        points=np.asarray(route['points'],dtype=float)
        if points.ndim!=2 or points.shape[1]!=3 or len(points)<2 or not np.isfinite(points).all():
            raise ValueError('Invalid native curve points: '+name)
        if not math.isfinite(float(route['width'])) or float(route['width'])<=0:
            raise ValueError('Invalid road width: '+name)
        entry=copy.deepcopy(old.get(name,{'name':name,'path':'assets/land_details/'+name+'.glb','native_source':'blender/road_kit/'+name+'.blend','position':[0,0,0]}))
        for field,extension in [('path','.glb'),('native_source','.blend')]:
            target=(root/entry[field]).resolve()
            if not target.is_relative_to(root.resolve()) or target.suffix!=extension:
                raise ValueError('Invalid road output '+field+': '+str(entry[field]))
        entries.append(entry)
    # Resolve all output collisions before creating directories or assets.
    selected_names={route['name'] for route in chosen}
    destinations={}
    for entry in merge_entries(existing,entries):
        for field in ['path','native_source']:
            target=str((root/entry[field]).resolve()).casefold()
            if target in destinations and (entry['name'] in selected_names or destinations[target] in selected_names):
                raise ValueError('Road output path shared with another asset: '+entry[field])
            destinations[target]=entry['name']
    return chosen,entries,existing,reports

def write_if_changed(path,value):
    if path.exists() and json.loads(path.read_text())==value:return
    path.parent.mkdir(parents=True,exist_ok=True)
    path.write_text(json.dumps(value,indent=2))
def cross(a,b):return a[0]*b[1]-a[1]*b[0]
def clip(polygon,triangle):
    sign=1 if cross(triangle[1]-triangle[0],triangle[2]-triangle[0])>0 else -1
    result=polygon
    for a,b in zip(triangle,np.roll(triangle,-1,axis=0)):
        source=result;result=[]
        if len(source)<3:break
        previous=source[-1];prior=sign*cross(b-a,previous-a)
        for p in source:
            value=sign*cross(b-a,p-a)
            if (value>=-1e-8)!=(prior>=-1e-8):result.append(previous+(p-previous)*(prior/(prior-value)))
            if value>=-1e-8:result.append(p)
            previous=p;prior=value
    return result
def plane_y(points,t):
    a,b,c=t
    den=(b[2]-c[2])*(a[0]-c[0])+(c[0]-b[0])*(a[2]-c[2])
    wa=((b[2]-c[2])*(points[:,0]-c[0])+(c[0]-b[0])*(points[:,1]-c[2]))/den
    wb=((c[2]-a[2])*(points[:,0]-c[0])+(a[0]-c[0])*(points[:,1]-c[2]))/den
    return wa*a[1]+wb*b[1]+(1-wa-wb)*c[1]
def terrain_cell(sampler,T,cx,cz):
    if (cx,cz) not in sampler.tiles:
        v,f=T.chunk_mesh(cx,cz);sampler.add(cx,cz,v,f)
    return sampler.tiles[(cx,cz)]
def build_route(route,entry,root,sampler,T):
    bpy.ops.object.select_all(action='SELECT');bpy.ops.object.delete(use_global=False)
    points=np.asarray(route['points'],dtype=float)[:,[0,2]]
    tangent=np.empty_like(points);tangent[0]=points[1]-points[0];tangent[-1]=points[-1]-points[-2];tangent[1:-1]=points[2:]-points[:-2]
    tangent/=np.maximum(np.linalg.norm(tangent,axis=1)[:,None],1e-8)
    offsets=np.c_[-tangent[:,1],tangent[:,0]]*route['width']*.5
    vertices=[];faces=[];max_error=0
    for i in range(len(points)-1):
        quad=np.array([points[i]+offsets[i],points[i]-offsets[i],points[i+1]-offsets[i+1],points[i+1]+offsets[i+1]])
        low=np.floor(quad.min(axis=0)/768).astype(int);high=np.floor(quad.max(axis=0)/768).astype(int)
        for cz in range(low[1],high[1]+1):
            for cx in range(low[0],high[0]+1):
                tris,buckets=terrain_cell(sampler,T,cx,cz);local=quad-[cx*768,cz*768]
                aa=np.clip(np.floor(local.min(axis=0)/24).astype(int),0,31);bb=np.clip(np.floor(local.max(axis=0)/24).astype(int),0,31)
                selected=set()
                for z in range(aa[1],bb[1]+1):
                    for x in range(aa[0],bb[0]+1):selected.update(buckets.get((x,z),[]))
                for index in selected:
                    tri=tris[index];polygon=np.asarray(clip(list(local),tri[:,[0,2]]))
                    if len(polygon)<3:continue
                    hh=plane_y(polygon,tri)+.10
                    if hh.min()<.5:continue
                    start=len(vertices)
                    vertices.extend(np.c_[polygon[:,0]+cx*768,hh,polygon[:,1]+cz*768].tolist())
                    for k in range(1,len(polygon)-1):
                        if abs(cross(polygon[k]-polygon[0],polygon[k+1]-polygon[0]))<1e-8:continue
                        faces.append((start,start+k,start+k+1))
                        centroid=polygon[[0,k,k+1]].mean(axis=0)
                        max_error=max(max_error,abs(hh[[0,k,k+1]].mean()-float(plane_y(centroid[None],tri)[0])-.10))
    name=route['name'];mesh=bpy.data.meshes.new(name+'Geometry')
    mesh.from_pydata([(p[0],-p[2],p[1]) for p in vertices],[],faces);mesh.update()
    bm=bmesh.new();bm.from_mesh(mesh);bmesh.ops.remove_doubles(bm,verts=list(bm.verts),dist=.0001);bmesh.ops.recalc_face_normals(bm,faces=list(bm.faces))
    for f in bm.faces:
        if f.normal.z<0:f.normal_flip()
    bm.to_mesh(mesh);bm.free();mesh.update()
    attr=mesh.color_attributes.new(name='Palette',type='FLOAT_COLOR',domain='CORNER')
    pigment=np.array([196,190,170])/255;linear=np.where(pigment<=.04045,pigment/12.92,((pigment+.055)/1.055)**2.4)
    for item in attr.data:item.color=(*linear,1)
    mesh.color_attributes.active_color_index=0;mesh.color_attributes.render_color_index=0
    mat=bpy.data.materials.new('Packed earth trail');mat.use_nodes=True;nt=mat.node_tree
    color=nt.nodes.new('ShaderNodeVertexColor');color.layer_name='Palette';bsdf=nt.nodes.get('Principled BSDF');bsdf.inputs['Roughness'].default_value=1
    nt.links.new(color.outputs['Color'],bsdf.inputs['Base Color']);mesh.materials.append(mat)
    obj=bpy.data.objects.new(name,mesh);bpy.context.scene.collection.objects.link(obj);obj.asset_mark();obj.select_set(True);bpy.context.view_layer.objects.active=obj
    path=root/entry['path'];native=root/entry['native_source']
    path.parent.mkdir(parents=True,exist_ok=True);native.parent.mkdir(parents=True,exist_ok=True)
    bpy.ops.export_scene.gltf(filepath=str(path),export_format='GLB',use_selection=True,export_apply=True,export_vertex_color='ACTIVE')
    bpy.ops.wm.save_as_mainfile(filepath=str(native))
    yy=sampler.height(points[:,0],points[:,1]);grade=np.abs(np.diff(yy))/np.maximum(np.linalg.norm(np.diff(points,axis=0),axis=1),1e-8)
    peak=int(grade.argmax());report={'name':name,'max_grade':float(grade[peak]),'steepest_segment':points[peak:peak+2].tolist(),'triangle_plane_error':max_error,'triangles':len(mesh.polygons)}
    print('ROAD MODULE',name,'triangles',len(mesh.polygons),'maximum grade',grade.max(),'triangle plane error',max_error,flush=True)
    return report

def main(argv=None,root=ROOT):
    if argv is None:argv=sys.argv[sys.argv.index('--')+1:] if '--' in sys.argv else []
    args=parse_args(argv)
    routes,entries,existing,previous_reports=prepare_build(root,args.road)
    global bpy,bmesh
    import bpy,bmesh
    sys.path.insert(0,str(root/'blender'))
    import terrain_topology as T
    sampler=T.SurfaceSampler()
    reports=[build_route(route,entry,root,sampler,T) for route,entry in zip(routes,entries)]
    write_if_changed(root/'assets/road_kit.json',merge_entries(existing,entries) if args.road else entries)
    write_if_changed(root/'captures/road-authoring-validation.json',merge_entries(previous_reports,reports) if args.road else reports)

if __name__=='__main__':main()
