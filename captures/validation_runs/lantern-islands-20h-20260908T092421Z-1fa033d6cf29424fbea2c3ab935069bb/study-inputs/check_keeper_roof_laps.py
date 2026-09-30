"""Read saved roof geometry and measure exposed top surfaces at overlapping courses."""
import bpy,json,hashlib
from pathlib import Path
root=Path(__file__).resolve().parents[1]
out=root/'reviews/round-20h-roof-laps.json';assert not out.exists()
def top_at(obj,x,y):
    zs=[]
    for tri in obj.data.loop_triangles:
        if tri.normal.z<.5:continue
        a,b,c=[obj.data.vertices[i].co for i in tri.vertices]
        denom=(b.y-c.y)*(a.x-c.x)+(c.x-b.x)*(a.y-c.y)
        if abs(denom)<1e-12:continue
        u=((b.y-c.y)*(x-c.x)+(c.x-b.x)*(y-c.y))/denom
        v=((c.y-a.y)*(x-c.x)+(a.x-c.x)*(y-c.y))/denom
        w=1-u-v
        if min(u,v,w)>=-1e-5:zs.append(u*a.z+v*b.z+w*c.z)
    assert zs,(obj.name,x,y)
    return max(zs)
rows=[]
for label in ['20g','20h']:
    path=root/'captures'/('lantern_islands_study_'+label)/'keeper_house.blend'
    bpy.ops.wm.open_mainfile(filepath=str(path));tiles=[]
    for obj in bpy.context.scene.objects:
        if not obj.name.startswith('Keeper staggered roof tile '):continue
        side,row,col=map(int,obj.name.split()[-3:]);obj.data.calc_loop_triangles()
        bounds=[min(v.co[i] for v in obj.data.vertices) for i in (0,1)]+[max(v.co[i] for v in obj.data.vertices) for i in (0,1)]
        tiles.append((obj,side,row,col,bounds))
    gaps=[]
    for a,side,row,col,ab in tiles:
        for b,bs,br,bc,bb in tiles:
            if bs!=side or br!=row+1:continue
            xmin,ymin=max(ab[0],bb[0]),max(ab[1],bb[1]);xmax,ymax=min(ab[2],bb[2]),min(ab[3],bb[3])
            if min(xmax-xmin,ymax-ymin)<1e-5:continue
            for fx,fy in [(.05,.05),(.95,.05),(.5,.5),(.05,.95),(.95,.95)]:
                x=xmin+(xmax-xmin)*fx;y=ymin+(ymax-ymin)*fy
                gap=top_at(a,x,y)-top_at(b,x,y)
                gaps.append({'upper':a.name,'lower':b.name,'xy':[x,y],'top_clearance_m':gap})
    rows.append({'label':label,'source_sha256':hashlib.sha256(path.read_bytes()).hexdigest(),'tile_count':len(tiles),'samples':len(gaps),'minimum_top_clearance_m':min(g['top_clearance_m'] for g in gaps),'maximum_top_clearance_m':max(g['top_clearance_m'] for g in gaps),'nonpositive_samples':sum(g['top_clearance_m']<=0 for g in gaps),'worst':sorted(gaps,key=lambda g:g['top_clearance_m'])[:8]})
result={'scope':'Five actual top-surface samples per overlapping adjacent course tile pair, saved Blender geometry. Checks exposed lap ordering, not all mesh intersections or visual acceptance.','passed':rows[1]['minimum_top_clearance_m']>.008,'versions':rows}
out.write_text(json.dumps(result,indent=2));print(json.dumps(result),flush=True)
