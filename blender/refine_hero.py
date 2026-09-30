"""Editable full-volume airship refinements; no camera projection or textures."""
import bpy,math,numpy as np
from mathutils import Vector,Matrix

def refine(api):
    mesh,box,rod=api['mesh'],api['box'],api['rod']
    library=api['library'];group=bpy.data.collections['Airship'];root=bpy.data.objects['Airship']
    lin,rgb=api['lin'],api['rgb']
    def ship(o,name):
        for c in list(o.users_collection):c.objects.unlink(o)
        group.objects.link(o);o.parent=root;o.name=name
        return o
    def paint(o,base,ambient=.70):
        colors=o.data.color_attributes.get('Palette')
        sun=Vector((-.48,-.30,.82)).normalized()
        for face in o.data.polygons:
            light=max(0,face.normal.dot(sun))
            c=lin(rgb(base)*(ambient+(1-ambient)*light))
            for k in face.loop_indices:colors.data[k].color=(*c,1)
    envelope=bpy.data.objects['Envelope']
    # Rotate the underlying ico topology before stretching it into the same
    # ellipsoid. Its irregular facet directions replace horizontal striping.
    turn=Matrix.Rotation(.27,3,'X')@Matrix.Rotation(.12,3,'Y')
    for vertex in envelope.data.vertices:
        p=vertex.co
        unit=Vector(((p.x-.3)/6.55,p.y/3.17,(p.z+p.x*.043-5)/4.2))
        q=turn@unit
        p.x=.3+q.x*6.55;p.y=q.y*3.17;p.z=5+q.z*4.2-p.x*.043
    envelope.data.update();paint(envelope,'e5cdb2',.68)
    # A complete tilted belt is the intersection of its plane and the gas
    # ellipsoid. Both edges and the underside are modeled as solid leather.
    for name in ['Leather belt 2','Belt stitching 2']:
        o=bpy.data.objects.get(name)
        if o:bpy.data.objects.remove(o,do_unlink=True)
    def band(name,offset,width,lift,color):
        vertices=[];faces=[];count=96
        for i in range(count):
            t=i*math.tau/count
            for thickness in [0,.042]:
                for side in [-1,1]:
                    a=-.92+offset+side*width/2;k=.35*3.23*math.sin(t)
                    aa=1+(k/6.55)**2;bb=2*(a-.3)*k/6.55**2;cc=((a-.3)/6.55)**2-1
                    r=(-bb+math.sqrt(bb*bb-4*aa*cc))/(2*aa)
                    z=(3.23*r+lift+thickness)*math.sin(t)
                    x=a+.35*z;y=5+(4.27*r+lift+thickness)*math.cos(t)-x*.043
                    vertices.append((x,y,z))
        for i in range(count):
            a=i*4;b=((i+1)%count)*4
            for u,v in [(0,1),(1,3),(3,2),(2,0)]:faces.append((a+u,a+v,b+v,b+u))
        return ship(mesh(vertices,faces,color),name)
    band('Leather belt 2',0,.23,.005,'76664d')
    band('Belt stitching 2',-.082,.019,.051,'b9a582')
    # Six genuinely separate planks wrap both sides of the curved hull.
    sections=[(-3.6,.16,-1.68,-2.1),(-2.8,1.02,-1.70,-3.55),(-1.45,1.24,-1.78,-3.9),(1.1,1.15,-1.80,-3.80),(2.7,.73,-1.52,-3.20),(3.45,.12,-1.17,-2.0)]
    for side in [-1,1]:
        for row in range(6):
            for index,(a,b) in enumerate(zip(sections[:-1],sections[1:])):
                v=[]
                for thickness in [0,.032]:
                    for x,w,top,bottom in [a,b]:
                        for f in [(row+.035)/6,(row+.965)/6]:
                            y=top*(1-f)+bottom*f;y=-1.6+(y+1.6)*1.19
                            z=side*(w*(1-.55*f*f)+.025+thickness)
                            v.append((x*1.16+.3,y,z))
                faces=[(0,2,3,1),(4,5,7,6),(0,1,5,4),(2,6,7,3),(0,4,6,2),(1,3,7,5)]
                o=ship(mesh(v,faces,['81664c','806147','8a6a4d'][row%3]),f'Hull plank {side} {row} {index}')
                paint(o,['81664c','806147','8a6a4d'][row%3],.80)
    for o in list(group.objects):
        if o.type!='MESH':continue
        if o.name.startswith(('Cabin upright','Cabin lintel','Window crossbar')):paint(o,'735b42',.77)
        if o.name.startswith('Rope swag'):paint(o,'978668',.78)
        if o.name=='Rigging':
            for v in o.data.vertices:
                if v.co.x<-6 and 2<v.co.z<6:v.co.z+=.55
        if o.name=='Flag':
            for v in o.data.vertices:
                v.co.x=.97+(v.co.x-.97)*1.08
                v.co.z=10.45+(v.co.z-10.45)*1.12-.28
                v.co.y+=math.sin((v.co.x-.97)*3.2)*.12
        if o.name=='Flagstaff':
            for v in o.data.vertices:v.co.z-=.25*max(0,(v.co.z-9)/2.7)
    for o in bpy.data.collections['Propeller'].objects:
        if o.type!='MESH':continue
        for v in o.data.vertices:
            radius=math.hypot(v.co.y,v.co.z)
            if radius<.4:continue
            angle=math.atan2(v.co.z,v.co.y);axis=round(angle/(math.pi/2))*(math.pi/2)
            angle=axis+(angle-axis)*1.55
            v.co.y=math.cos(angle)*radius;v.co.z=math.sin(angle)*radius
    print('AIRSHIP: irregular envelope, tilted solid belt, 60 curved hull planks and refined fittings',flush=True)
