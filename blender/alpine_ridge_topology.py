"""Closed alpine meshes from separately authored ridge and drainage networks.

The coordinates are normalized modelling controls. Their metre-space assets
retain the existing prefab origins; Godot continues to own scene placement.
"""
import math
import numpy as np
from mathutils import Vector
from mathutils.geometry import delaunay_2d_cdt

# Each chain is a section through an actual ridge, with unequal saddles and
# secondary summits. No shared rings radiate outwards from the highest point.
# Point order is x, z, height relative to that module's measured dimensions.
SPINES=[
 [(-.47,-.71,.10),(-.25,-.43,.43),(-.12,-.19,.78),(0,0,1),(.11,.14,.79),(.31,.30,.64),(.35,.63,.20)],
 [(-.25,-.75,.09),(-.23,-.45,.50),(-.08,-.17,.86),(0,0,1),(.13,.19,.67),(.06,.46,.54),(.30,.71,.10)],
 [(-.43,-.70,.10),(-.27,-.43,.39),(-.09,-.21,.66),(0,0,1),(.12,.17,.66),(.32,.36,.41),(.44,.66,.10)],
 [(-.44,-.65,.11),(-.27,-.43,.46),(-.20,-.19,.70),(0,0,1),(.18,.11,.84),(.29,.36,.42),(.42,.66,.08)],
 [(-.61,-.56,.10),(-.38,-.36,.33),(-.19,-.14,.77),(0,0,1),(.22,.11,.79),(.40,.32,.39),(.44,.67,.09)],
 [(-.39,-.71,.09),(-.29,-.40,.39),(-.10,-.16,.82),(0,0,1),(.12,.21,.83),(.20,.43,.44),(.40,.67,.10)],
 [(-.39,-.72,.10),(-.25,-.44,.47),(-.16,-.15,.83),(0,0,1),(.19,.11,.83),(.21,.44,.43),(.39,.65,.10)],
 [(-.54,-.64,.09),(-.31,-.38,.34),(-.13,-.16,.71),(0,0,1),(.20,.12,.78),(.35,.34,.56),(.45,.67,.12)],
 [(-.28,-.78,.10),(-.21,-.47,.34),(-.10,-.19,.81),(0,0,1),(.10,.21,.84),(.17,.43,.52),(.35,.73,.09)],
 [(-.49,-.68,.10),(-.35,-.41,.54),(-.19,-.16,.78),(0,0,1),(.20,.14,.71),(.29,.37,.59),(.40,.69,.12)],
 [(-.43,-.67,.08),(-.32,-.41,.45),(-.14,-.19,.73),(0,0,1),(.19,.15,.85),(.30,.40,.44),(.36,.71,.09)]
]

def make_massif(index,rx,rz,height):
    points=[];edges=[]
    def point(x,z,h):
        p=(float(x),float(z),float(h))
        for i,q in enumerate(points):
            if abs(p[0]-q[0])+abs(p[1]-q[1])<1e-8:return i
        points.append(p);return len(points)-1
    def chain(values):
        ids=[point(*p) for p in values]
        edges.extend(zip(ids[:-1],ids[1:]));return ids
    outline=[(-.90,-.59),(-.44,-.94),(.16,-.93),(.68,-.66),(.95,-.16),(.87,.34),(.55,.74),(.03,.96),(-.51,.82),(-.90,.40),(-1,-.06)]
    # Low closed foundations have different shoulder widths on each side.
    outline=[(x*(1+.06*math.sin(index*2+i)),z*(1+.06*math.cos(index+i*2))) for i,(x,z) in enumerate(outline)]
    border=[point(x,z,-.012) for x,z in outline]
    edges.extend(zip(border,border[1:]+border[:1]))
    spine=list(SPINES[index])
    # Measured principal crests have a lower col before a secondary summit.
    # Keep each highest point fixed while giving selected modules a true
    # descending-then-ascending profile, rather than naming a shoulder a col.
    if index in [0,1,3,6,9]:
        x,z,_=spine[4];spine[4]=(x,z,[.43,.45,.46,.44,.42][[0,1,3,6,9].index(index)])
        x,z,_=spine[5];spine[5]=(x,z,[.64,.61,.67,.62,.61][[0,1,3,6,9].index(index)])
    chain(spine)
    shift=.045*math.sin(index*1.7)
    chain([spine[1],(-.53,-.46,.31),(-.72,-.29,.12),(-.90,-.19,.02)])
    chain([spine[2],(.13,-.33,.64),(.38,-.47,.40),(.58,-.62,.05)])
    chain([spine[3],(-.22,.08+shift,.75),(-.42,.22,.54),(-.64,.43,.25),(-.76,.48,.04)])
    chain([spine[4],(.44,.07,.55),(.63,.15,.33),(.82,.21,.04)])
    chain([spine[5],(.03,.52,.37),(-.20,.67,.19),(-.31,.80,.03)])
    # Drainage floors sit between ridges and descend independently. Upper
    # cirque floors, lower knees and valley mouths prevent long flat skirts.
    chain([(-.31,-.21,.49),(-.52,-.16,.23),(-.76,-.03,.07)])
    chain([(.07,-.14,.72),(.29,-.19,.34),(.63,-.22,.06)])
    chain([(-.12,.18,.59),(-.25,.38,.32),(-.44,.61,.06)])
    chain([(.27,.23,.50),(.48,.39,.27),(.64,.53,.05)])
    # Rear cirque, visible when the player circles behind the mountain.
    chain([(-.04,-.43,.35),(.01,-.64,.20),(.18,-.79,.04)])
    # A recessed upper cirque cuts the broad front snow face into a steep
    # headwall and unequal lateral ribs; these are actual displaced vertices.
    chain([(.01,.045,.78),(-.025,.11,.62),(-.095,.22,.43)])
    chain([(-.095,-.035,.86),(-.15,.01,.70),(-.26,.04,.56)])
    for p in [(.20,-.065,.67),(.27,.055,.52),(-.29,-.08,.44)]:point(*p)
    for p in [(-.54,-.66,.10),(.35,-.71,.13),(-.77,.21,.08),(-.07,.82,.06)]:point(*p)
    coords=[Vector((p[0]*rx,p[1]*rz)) for p in points]
    xy,_,triangles,original,_,_=delaunay_2d_cdt(coords,edges,[],0,.00001,True)
    verts=[]
    for p,ids in zip(xy,original):
        if ids:h=sum(points[i][2] for i in ids)/len(ids)
        else:
            # A rare crossing splits a ridge segment. Interpolate its actual
            # control heights; do not sample an unrelated radial formula.
            values=[]
            for a,b in edges:
                aa=np.array(coords[a]);bb=np.array(coords[b]);d=bb-aa
                t=np.clip(np.dot(np.array(p)-aa,d)/max(np.dot(d,d),1e-12),0,1)
                if np.linalg.norm(np.array(p)-aa-d*t)<.001:values.append(points[a][2]*(1-t)+points[b][2]*t)
            assert values,(index,list(p))
            h=sum(values)/len(values)
        verts.append([p.x,h*height,p.y])
    faces=[tuple(t) for t in triangles]
    # Detect the true perimeter after CDT, including any split edges, and
    # close the complete volume down to a welded common foundation.
    counts={}
    for f in faces:
        for a,b in zip(f,f[1:]+f[:1]):
            key=tuple(sorted((a,b)));counts[key]=counts.get(key,0)+1
    boundary=[e for e,n in counts.items() if n==1]
    bottom={}
    for a,b in boundary:
        for i in [a,b]:
            if i not in bottom:
                bottom[i]=len(verts);verts.append([verts[i][0],-12,verts[i][2]])
        faces.extend([(a,b,bottom[b]),(a,bottom[b],bottom[a])])
    center=len(verts);verts.append([0,-12,0])
    for a,b in boundary:faces.append((bottom[b],bottom[a],center))
    return verts,faces
