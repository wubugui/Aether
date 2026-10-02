"""Pure affine bounds. No engine, filesystem writes or inferred active physics."""
import math,struct

def require(ok,label):
    if not ok: raise ValueError(label)

def f32(x):
    require(math.isfinite(x),'nonfinite input')
    y=struct.unpack('<f',struct.pack('<f',x))[0]
    require(math.isfinite(y),'float32 overflow')
    return y

def bounds_ok(b):
    return (type(b)is dict and set(b)=={'min','max'} and all(type(b[k])is list and len(b[k])==3 for k in b)
            and all(type(x)in(int,float)and math.isfinite(x)for k in b for x in b[k]) and all(b['min'][i]<=b['max'][i]for i in range(3)))

def union(*boxes):
    boxes=[b for b in boxes if b is not None];require(boxes and all(bounds_ok(b)for b in boxes),'invalid union')
    return {'min':[min(b['min'][i]for b in boxes)for i in range(3)],'max':[max(b['max'][i]for b in boxes)for i in range(3)]}

def hits(b,q):
    require(bounds_ok(b),'invalid query bounds');require(len(q)==4 and all(math.isfinite(x)for x in q)and q[0]<=q[1]and q[2]<=q[3],'invalid rectangle')
    return b['max'][0]>=q[0]and b['min'][0]<=q[1]and b['max'][2]>=q[2]and b['min'][2]<=q[3]

def row_to_columns(r):
    require(len(r)>=12 and all(math.isfinite(x)for x in r),'invalid buffer row')
    return [r[i]for i in (0,4,8,1,5,9,2,6,10,3,7,11)]

def transform_box_native(t,b):
    """4.5.1 Transform3D::xform(AABB), then AABB.end, explicit binary32 steps."""
    require(len(t)==12 and all(math.isfinite(x)for x in t)and bounds_ok(b),'invalid affine box')
    lo=[];hi=[]
    for i in range(3):
        a=z=t[9+i]
        for j in range(3):
            e=f32(t[j*3+i]*b['min'][j]);f=f32(t[j*3+i]*b['max'][j])
            a=f32(a+min(e,f));z=f32(z+max(e,f))
        lo.append(a);hi.append(f32(a+f32(z-a)))
    return {'min':lo,'max':hi}

def transform_box_outer(t,b):
    """Directed binary64 interval enclosure of affine local AABB; no epsilon."""
    require(len(t)==12 and all(math.isfinite(x)for x in t)and bounds_ok(b),'invalid affine box')
    lo=[];hi=[]
    for i in range(3):
        a=z=t[9+i]
        for j in range(3):
            e=t[j*3+i]*b['min'][j];f=t[j*3+i]*b['max'][j]
            a=math.nextafter(a+math.nextafter(min(e,f),-math.inf),-math.inf)
            z=math.nextafter(z+math.nextafter(max(e,f),math.inf),math.inf)
        lo.append(a);hi.append(z)
    return {'min':lo,'max':hi}

def tree_capsule_box(t):
    # Enclose decimal authoring value and its float32 representation.
    # No active physics-server scaling/decomposition behavior is inferred.
    r=max(2.4,f32(2.4));local={'min':[-r,0.,-r],'max':[r,11.,r]}
    return union(transform_box_outer(t,local),transform_box_native(t,local))
