"""Deterministic, renderer-independent source geometry for a FOUR-root cloud bank.

This module writes nothing on import. Coordinates here are Godot world metres.
It is a bounded volume design, never a whole-world generator or image backdrop.
"""
from copy import deepcopy
from math import sin, cos, pi, sqrt, exp

SCHEMA = 'cloud-bank58-source-v1'
DOMAIN = (2625.0, 2425.0, 4925.0, 4725.0)  # x min, z min, x max, z max
STEPS = 18  # 63.89m authored low-poly spacing per 1150m root span
ROOTS = [('CloudSea_0_0', 0, 0), ('CloudSea_1_0', 1, 0),
         ('CloudSea_0_1', 0, 1), ('CloudSea_1_1', 1, 1)]

# Each ridge is one editable POLY spline. Points hold world x,z, added height,
# half-width. Unequal heights/widths along a shared crest prevent sphere rows.
RIDGES = [
    dict(name='near_overfold', points=[(2690,4270,140,210), (3010,4030,270,270),
         (3380,4190,210,240), (3630,3930,170,190)], power=.90),
    dict(name='middle_fork', points=[(3340,2910,110,150), (3540,3170,205,205),
         (3810,3430,265,245), (4140,3380,180,170), (4480,3640,115,140)], power=1.10),
    dict(name='far_broken_rim', points=[(3910,2600,90,110), (4150,2780,155,145),
         (4410,2710,105,115), (4640,2920,130,120), (4830,2850,75,95)], power=1.10),
    dict(name='right_return_fold', points=[(4380,4110,155,210), (4670,4380,230,250),
         (4870,4170,130,190)], power=.90),
]
VALLEYS = [
    dict(name='diagonal_flying_trough', points=[(2900,4530,115,160), (3220,4210,120,145),
         (3500,3850,160,190), (3900,3760,150,165), (4220,3270,130,145),
         (4640,3110,105,115)], power=1.25),
    dict(name='transverse_lightning_fold', points=[(2770,3390,120,120), (3150,3500,155,150),
         (3410,3360,170,140), (3710,3150,155,115), (3970,3020,110,95)], power=1.10),
]
# Angular accent peaks are a minority of the total bank surface. Their support
# radii decrease across the diagonal depth axis, so foreground and distant relief
# are not clones. They are integrated into the bank, never scattered ico-spheres.
PEAKS = [
    dict(name='near_split_peak', center=(3050,4040), radii=(170,145), height=115),
    dict(name='near_low_shoulder', center=(3340,4190), radii=(130,155), height=60),
    dict(name='middle_blunt_peak', center=(3820,3430), radii=(130,120), height=90),
    dict(name='middle_spur', center=(4140,3380), radii=(115,90), height=65),
    dict(name='far_needle', center=(4160,2760), radii=(85,70), height=80),
    dict(name='far_small_spur', center=(4640,2900), radii=(75,75), height=60),
    dict(name='right_crest_peak', center=(4660,4370), radii=(155,120), height=100),
]
# Closed upper ribbons. Their below/above topology is native, 3D and thick;
# width/thickness and sparse crest knots make them horizontal banks with spikes.
SHELVES = [
    dict(name='upper_west_layer', root='CloudSea_0_0',
         points=[(2710,2940,1490,125,30,30), (3000,2820,1510,150,35,105),
                 (3320,2760,1500,105,23,20), (3540,2680,1525,65,18,65)], sides=8),
    dict(name='upper_east_layer', root='CloudSea_1_1',
         points=[(4120,4110,1650,70,22,35), (4380,4040,1630,130,32,100),
                 (4650,3930,1630,140,30,25), (4890,3760,1660,75,21,90)], sides=8),
    dict(name='upper_far_veil', root='CloudSea_1_0',
         points=[(3800,2630,1365,45,14,15), (4090,2500,1370,80,21,60),
                 (4400,2465,1355,95,20,20), (4810,2550,1375,55,15,45)], sides=8),
]


def recipe():
    return deepcopy(dict(schema=SCHEMA, domain=list(DOMAIN), steps=STEPS,
                         ridges=RIDGES, valleys=VALLEYS, peaks=PEAKS, shelves=SHELVES))


def polyline_value(x, z, row):
    """Compact angular ridge, with smoothly varying crest height and half-width."""
    best = 0.0
    points = row['points']
    for a, b in zip(points, points[1:]):
        dx, dz = b[0]-a[0], b[1]-a[1]
        t = max(0., min(1., ((x-a[0])*dx+(z-a[1])*dz)/(dx*dx+dz*dz)))
        distance = sqrt((x-a[0]-t*dx)**2+(z-a[1]-t*dz)**2)
        width = a[3]*(1-t)+b[3]*t
        height = a[2]*(1-t)+b[2]*t
        best = max(best, height*max(0., 1-distance/width)**row['power'])
    return best


def surfaces(x, z, spec):
    # Broad continuous lower mass: no common flat top or bottom, and no hole
    # punched through the bank. Valley values carve relief but retain real cloud.
    base = 710 + 33*sin((x-2500)/390)*cos((z-2200)/310) + 22*sin((x+z)/220)
    ridge = max(polyline_value(x,z,r) for r in spec['ridges'])
    valley = max(polyline_value(x,z,r) for r in spec['valleys'])
    accents = 0.
    for p in spec['peaks']:
        dx=abs((x-p['center'][0])/p['radii'][0]); dz=abs((z-p['center'][1])/p['radii'][1])
        accents=max(accents,p['height']*max(0.,1-(dx**1.3+dz**1.3)**(1/1.3)))
    # Low oblique folds are subordinate to the authored ridges, not random noise.
    fold = 18*sin((x-.43*z)/92) + 11*sin((z+.31*x)/71)
    top = base+ridge+accents-valley+fold
    bottom = 335 + 52*sin((x-2450)/305)*cos((z-2300)/335) - 39*cos((x+.65*z)/230)
    return top, bottom


def surface_xy(i, j, spec):
    """Stable shared lattice including non-rectangular outer footprint."""
    n=spec['steps']*2; xmin,zmin,xmax,zmax=spec['domain']
    u=i/n; v=j/n
    x=xmin+(xmax-xmin)*u; z=zmin+(zmax-zmin)*v
    # Same formula on both sides of every root seam. Irregular broad perimeter
    # and staggered interior vertices keep obvious square rows out of silhouettes.
    x += 48*sin(2*pi*v+.35) + 24*sin(7*pi*v) + 15*sin(i*1.7+j*2.3)*sin(pi*u)
    z += 43*sin(2*pi*u-.6) + 21*sin(5*pi*u) + 15*cos(i*2.1-j*1.3)*sin(pi*v)
    return x,z


def lower_point(i, j, spec):
    x,z=surface_xy(i,j,spec); n=spec['steps']*2
    # The outer belly curls inward. Shared inner edges retain exact common xz.
    dx=65*exp(-i/1.1)-65*exp(-(n-i)/1.1)
    dz=65*exp(-j/1.1)-65*exp(-(n-j)/1.1)
    return x+dx,z+dz


def bank_tile(name, tx, tz, spec, cap_internal=True):
    steps=spec['steps']; vertices=[]; faces=[]; roles=[]
    for surface in ('top','bottom'):
        for j in range(steps+1):
            for i in range(steps+1):
                gx=tx*steps+i; gz=tz*steps+j
                x,z=surface_xy(gx,gz,spec)
                y=surfaces(x,z,spec)[surface=='bottom']
                if surface=='bottom': x,z=lower_point(gx,gz,spec)
                vertices.append((x,y,z)); roles.append(surface)
    size=(steps+1)**2
    for j in range(steps):
        for i in range(steps):
            a=j*(steps+1)+i; b=a+1; c=a+steps+1; d=c+1
            if (i+j+tx+tz)%2:
                pair=[(a,c,d),(a,d,b)]
            else: pair=[(a,c,b),(b,c,d)]
            faces.extend(pair)
            faces.extend(tuple(k+size for k in reversed(t)) for t in pair)
    # Clockwise perimeter in x/z. Two additional belts round the exposed side
    # as an irregular fold, not a rectangular vertical skirt. Internal caps
    # match exactly and are buried in the assembled four-volume union.
    perimeter=[i for i in range(steps+1)]
    perimeter += [j*(steps+1)+steps for j in range(1,steps+1)]
    perimeter += [steps*(steps+1)+i for i in range(steps-1,-1,-1)]
    perimeter += [j*(steps+1) for j in range(steps-1,0,-1)]
    loops=[perimeter]
    for fraction in (.30,.72):
        ring=[]
        for k in perimeter:
            j,i=divmod(k,steps+1); gx=tx*steps+i;gz=tz*steps+j;n=steps*2
            top=vertices[k];bottom=vertices[k+size]
            bulge=sin(pi*fraction)*(32+13*sin((top[0]+top[2])/83))
            ox=(-1 if gx==0 else 1 if gx==n else 0)*bulge
            oz=(-1 if gz==0 else 1 if gz==n else 0)*bulge
            co=tuple(top[q]*(1-fraction)+bottom[q]*fraction for q in range(3))
            ring.append(len(vertices));vertices.append((co[0]+ox,co[1],co[2]+oz));roles.append('folded_side')
        loops.append(ring)
    loops.append([k+size for k in perimeter])
    for a,b in zip(loops,loops[1:]):
        for k in range(len(perimeter)):
            t=(k+1)%len(perimeter)
            ja,ia=divmod(perimeter[k],steps+1);jb,ib=divmod(perimeter[t],steps+1)
            interior=((ia==ib==0 and tx==1) or (ia==ib==steps and tx==0)
                      or (ja==jb==0 and tz==1) or (ja==jb==steps and tz==0))
            if cap_internal or not interior:
                faces += [(a[k],a[t],b[t]),(a[k],b[t],b[k])]
    return dict(name='CloudBank58_'+name.removeprefix('CloudSea_')+'_volume',root=name,
                kind='continuous_lower_volume', vertices=vertices,faces=faces,roles=roles,
                seam_lattice={'tx':tx,'tz':tz,'steps':steps}, top_count=size)


def continuous_bank(spec):
    """Weld four native regions, omit ALL internal caps, retain region groups.

    One LOCAL closed volume spans four roots. No coplanar caps, buried duplicate
    surfaces, overlapping tiled tops, boolean remeshing, or full-world geometry.
    """
    vertices=[];faces=[];roles=[];regions={};index={}
    for name,tx,tz in ROOTS:
        tile=bank_tile(name,tx,tz,spec,cap_internal=False);mapping={};group=set()
        for face in tile['faces']:
            for vi in face:
                if vi in mapping:continue
                co=tile['vertices'][vi]
                if co not in index:
                    index[co]=len(vertices);vertices.append(co);roles.append(tile['roles'][vi])
                mapping[vi]=index[co];group.add(index[co])
            faces.append(tuple(mapping[vi] for vi in face))
        regions[name]=sorted(group)
    return dict(name='CloudBank58_four_root_continuous_volume',root='CloudSea_0_0',
                kind='continuous_lower_volume',vertices=vertices,faces=faces,roles=roles,
                native_region_vertex_groups=regions,internal_caps=0,
                welded_vertex_count=sum(len(bank_tile(n,x,z,spec,False)['vertices']) for n,x,z in ROOTS)-len(vertices))


def shelf_mesh(row):
    vertices=[];faces=[];roles=[];rings=[];points=row['points']; sides=row['sides']
    # Nine subdivisions per path interval; rings taper naturally at both ends.
    samples=[]
    for seg,(a,b) in enumerate(zip(points,points[1:])):
        for step in range(6):
            t=step/6;samples.append(tuple(a[q]*(1-t)+b[q]*t for q in range(6)))
    samples.append(tuple(points[-1]))
    for k,p in enumerate(samples):
        prev=samples[max(0,k-1)];nxt=samples[min(len(samples)-1,k+1)]
        dx,dz=nxt[0]-prev[0],nxt[1]-prev[1];length=sqrt(dx*dx+dz*dz)
        nx,nz=-dz/length,dx/length;ring=[]
        taper=.12+.88*min(1.,k/2.,(len(samples)-1-k)/2.)
        for s in range(sides):
            theta=2*pi*s/sides;c=cos(theta);up=sin(theta)
            across=p[3]*c*taper
            y=p[2]+p[4]*up*taper
            # Sparse high crests are on the upper side only. Six-segment path
            # interpolation gives asymmetric faceted crests, never dome repeats.
            if up>0:y+=p[5]*(up**3)*taper*(.7+.3*cos(k*1.41))
            y+=4*sin(k*1.7+s*1.1)*taper
            ring.append(len(vertices));vertices.append((p[0]+nx*across,y,p[1]+nz*across));roles.append('upper_fold')
        rings.append(ring)
    for a,b in zip(rings,rings[1:]):
        for s in range(sides):
            t=(s+1)%sides;faces += [(a[s],b[s],b[t]),(a[s],b[t],a[t])]
    for end,reverse in ((0,True),(-1,False)):
        ring=rings[end];p=samples[end];center=len(vertices);vertices.append((p[0],p[2],p[1]));roles.append('upper_cap')
        for s in range(sides):
            t=(s+1)%sides
            faces.append((center,ring[t],ring[s]) if reverse else (center,ring[s],ring[t]))
    # Normalize winding with actual signed volume, so mirrored paths stay valid.
    if signed_volume(vertices,faces)<0:faces=[tuple(reversed(f)) for f in faces]
    return dict(name='CloudBank58_'+row['name'],root=row['root'],kind='closed_upper_ribbon',vertices=vertices,faces=faces,roles=roles)


def signed_volume(vertices,faces):
    # Translate to local origin before summation for stable metre-scale volume.
    o=vertices[0];v=[tuple(p[q]-o[q] for q in range(3)) for p in vertices]
    total=0.
    for ia,ib,ic in faces:
        a,b,c=v[ia],v[ib],v[ic]
        total+=a[0]*(b[1]*c[2]-b[2]*c[1])+a[1]*(b[2]*c[0]-b[0]*c[2])+a[2]*(b[0]*c[1]-b[1]*c[0])
    return total/6


def meshes(spec=None):
    spec=recipe() if spec is None else spec
    return [continuous_bank(spec)]+[shelf_mesh(s) for s in spec['shelves']]
