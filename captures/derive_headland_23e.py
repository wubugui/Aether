from pathlib import Path
root=Path(__file__).resolve().parents[1]
text=(root/'blender/model_headland_23d.py').read_text(encoding='utf-8').replace('headland_study_23d','headland_study_23e').replace("'label':'23d'","'label':'23e'")
old='d,h=min(coast);return d,h,min(seams)'
new='''d,h=min(coast)
    weights=[(1/max(.02,dd)**3,yy) for dd,yy in coast]
    continuous=sum(w*y for w,y in weights)/sum(w for w,y in weights)
    return d,continuous,min(seams)'''
assert old in text;text=text.replace(old,new)
old='target=max(old+.05,authored)'
new='''# Asymmetric authored rock ridges, separate from the shoreline interpolation.
    spines=[(-2177,-1720,40,48,34,-.35),(-2180,-1780,48,50,53,-.22),(-2142,-1820,34,60,44,.40),(-2180,-1890,40,48,57,.18),(-2210,-1962,31,34,58,-.2)]
    ridge_height=authored
    for rx,rz,peak,wx,wz,angle in spines:
        co,si=math.cos(angle),math.sin(angle);u=co*(x-rx)-si*(z-rz);v=si*(x-rx)+co*(z-rz)
        radius=max(abs(u)/wx,abs(v)/wz)
        ridge_height=max(ridge_height,authored+(peak-authored)*max(0,1-radius)**1.35)
    target=max(old+.05,ridge_height)'''
assert old in text;text=text.replace(old,new)
# Remove repetitive center fans; differing diagonal choice retains a single solid side.
start=text.index('    if distance<.02 and seam>2:')
end=text.index("terrain=mesh(",start)
text=text[:start]+'''    if distance<.02 and seam>2:
        if (a+b)%2:faces.extend([(a,b,b+n),(a,b+n,a+n)])
        else:faces.extend([(a,b,a+n),(b,b+n,a+n)])
        tags.extend(['cliff','cliff'])
    else:faces.append((a,b,b+n,a+n));tags.append('buried_seam')
'''+text[end:]
# Add actual broad shoreline buttresses, with feet embedded in surveyed ocean bed.
anchor="freeze('mainland_headland'"
start=text.index(anchor)
rocks='''# Closed asymmetrical rock masses; designed below nearby house pads, not loose visual triangles.
rock_specs=[(-2272,-1742,10,9,4.2,-.25),(-2273,-1765,9,12,4.6,.3),(-2260,-1787,12,7,5.8,-.4),(-2240,-1806,11,7,3.4,.2),(-2204,-1828,7,10,2.,-.3),(-2224,-1849,10,7,2.4,.4),(-2250,-1864,8,9,3.,.5),(-2255,-1885,8,12,3.7,-.2),(-2238,-1907,10,8,6.2,.4),(-2226,-1940,8,9,4.3,.2),(-2260,-1990,8,12,5.3,-.3)]
rock_records=[]
for number,(x,z,wx,wz,top,angle) in enumerate(rock_specs):
    # Hand-shaped eight-vertex shoulder with tilted crown and an uneven seaward nose.
    local=[(-.92,-.6,-10),(.77,-.83,-10),(1.,.72,-10),(-.68,.96,-10),(-.62,-.47,top-.8),(.48,-.7,top+.6),(.66,.39,top-.2),(-.40,.58,top+1.2),(-1.13,.05,top-2.8)]
    co,si=math.cos(angle),math.sin(angle);vertices=[]
    for u,v,y in local:
        px=x+co*u*wx+si*v*wz;pz=z-si*u*wx+co*v*wz
        vertices.append((px-origin[0],-(pz-origin[2]),y))
    bm=bmesh.new()
    for p in vertices:bm.verts.new(p)
    bmesh.ops.convex_hull(bm,input=list(bm.verts),use_existing_faces=False)
    bm.verts.ensure_lookup_table();bm.verts.index_update()
    obj=mesh('Broad tidal buttress '+str(number),[tuple(v.co) for v in bm.verts],[tuple(v.index for v in f.verts) for f in bm.faces],rock);bm.free()
    obj.data.materials.append(rockface);obj.data.materials.append(rockdark)
    for polygon in obj.data.polygons:polygon.material_index=2 if polygon.center.z<-.6 else (1 if polygon.normal.x>.35 else 0)
    rock_records.append({'name':obj.name,'center':[x,0,z],'crown_y_max':top+1.2,'base_y':-10})
(OUT/'rock-buttresses.json').write_text(json.dumps(rock_records,indent=2))
'''
text=text[:start]+rocks+text[start:]
target=root/'blender/model_headland_23e.py';assert not target.exists();target.write_text(text,encoding='utf-8')
