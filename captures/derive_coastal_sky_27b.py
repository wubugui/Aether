from pathlib import Path
R=Path(__file__).resolve().parents[1]
p=(R/'blender/model_coastal_sky_27a.py').read_text().replace("OUT=ROOT/'captures/coastal_sky_assets_27a'","OUT=ROOT/'captures/coastal_sky_assets_27b'")
start=p.index('def lobe(');end=p.index('clouds=[',start)
p=p[:start]+'''def lobe(name,center,size,turn):
    # Coherent sculpted cross-sections keep a rounded underside and an uneven
    # roof ridge. No single broad convex-hull plane spans the visible cloud.
    cx,cy,cz=center;rx,ry,h=size;h*=1.35;co,si=math.cos(turn),math.sin(turn)
    sections=[(-1.,.035),(-.72,.62),(-.34,.90),(.05,1.),(.40,.84),(.72,.57),(1.,.035)]
    count=12;points=[]
    for j,(x,spread) in enumerate(sections):
        ridge=1.+.13*math.sin(j*1.7+turn*3.)
        for k in range(count):
            angle=2*math.pi*k/count
            u=x*rx;v=math.cos(angle)*ry*spread
            z=cz+h*(.05+.13*spread+math.sin(angle)*spread*(.84*ridge if math.sin(angle)>=0 else .43))
            points.append((cx+co*u-si*v,cy+si*u+co*v,z))
    faces=[tuple(reversed(range(count)))]
    for j in range(len(sections)-1):
        for k in range(count):
            a=j*count+k;b=j*count+(k+1)%count;c=(j+1)*count+(k+1)%count;d=(j+1)*count+k
            if (j+k)%2:faces.extend([(a,b,d),(b,c,d)])
            else:faces.extend([(a,b,c),(a,c,d)])
    faces.append(tuple((len(sections)-1)*count+k for k in range(count)))
    data=bpy.data.meshes.new(name);data.from_pydata(points,[],faces);data.update()
    obj=bpy.data.objects.new(name,data);bpy.context.collection.objects.link(obj)
    obj.data.materials.append(material('Cloud silver vapor',(.75,.81,.91)))
'''+p[end:]
p=p.replace('New editable cloud volumes have taller lobes and beveled asymmetric undersides, removing the single flat underside silhouette.','New editable cloud lobes use seven shaped cross-sections and twelve radial samples with an asymmetric ridge and rounded underside;27a flat-hull cloud prototype retained separately.')
(R/'blender/model_coastal_sky_27b.py').write_text(p,encoding='utf-8')
g=(R/'captures/check_coastal_sky_27a.py').read_text().replace('27a','27b');(R/'captures/check_coastal_sky_27b.py').write_text(g,encoding='utf-8')
