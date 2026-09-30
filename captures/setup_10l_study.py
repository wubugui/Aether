from pathlib import Path
root=Path('D:/test6');out=root/'captures'
source=(out/'seat_10k_plateau.py').read_text().replace('10k','10l')
marker="obj=bpy.data.objects['cliff_eastern_plateau'];mesh=obj.data;origin=np.array(item['position'])"
snapshot='''
# Preserve the native artist vertex paint when retopologizing its contact band.
# Sampling is on the prior 3D asset's surface, never on a reference image.
paint_tri=[];paint_colors=[]
prior_paint=mesh.color_attributes['Palette']
for face in mesh.polygons:
    triangle=np.array([mesh.vertices[k].co for k in face.vertices])
    if triangle[:,2].min()< -14 or abs(np.cross(triangle[1,:2]-triangle[0,:2],triangle[2,:2]-triangle[0,:2]))<1e-6:continue
    paint_tri.append(triangle[:,:2]);paint_colors.append(np.mean([prior_paint.data[k].color[:3] for k in face.loop_indices],axis=0))
paint_tri=np.array(paint_tri);paint_colors=np.array(paint_colors)
pa,pb,pc=paint_tri[:,0],paint_tri[:,1],paint_tri[:,2]
den=(pb[:,1]-pc[:,1])*(pa[:,0]-pc[:,0])+(pc[:,0]-pb[:,0])*(pa[:,1]-pc[:,1])
def inherited_paint(center):
    x,y=center[:2]
    u=((pb[:,1]-pc[:,1])*(x-pc[:,0])+(pc[:,0]-pb[:,0])*(y-pc[:,1]))/den
    v=((pc[:,1]-pa[:,1])*(x-pc[:,0])+(pa[:,0]-pc[:,0])*(y-pc[:,1]))/den
    candidates=np.flatnonzero((u>=-1e-4)&(v>=-1e-4)&(u+v<=1+1e-4))
    index=candidates[0] if len(candidates) else np.argmin(np.sum((paint_tri.mean(1)-[x,y])**2,axis=1))
    return paint_colors[index]
'''
source=source.replace(marker,marker+snapshot)
source=source.replace("    for k in face.loop_indices:attr.data[k].color=(*c,1)", "    if face.normal.z>1e-5:c=inherited_paint(face.center)\n    for k in face.loop_indices:attr.data[k].color=(*c,1)")
(out/'seat_10l_plateau.py').write_text(source)
(out/'check_10l_plateau.py').write_text((out/'check_10k_plateau.py').read_text().replace('10k','10l'))
