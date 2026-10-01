"""Native closed 3D folded-volume controls. No rectangular domain or heightfield.

Each section: x,y,z, lateral half-width, upper height, lower depth, roll degrees.
Unequal asymmetric cross sections and paths define the outside silhouette.
"""
from math import sin,cos,radians,sqrt
PROFILE=[(1,.08),(.87,.51),(.47,.83),(.08,1),(-.36,.78),(-.79,.43),
         (-1,-.02),(-.82,-.49),(-.43,-.87),(.04,-1),(.57,-.71),(.9,-.30)]
LOFTS=[
 ('deep_wide_saddle',[(2590,465,3570,25,40,50,0),(2960,445,3540,390,130,210,-7),(3450,450,3500,520,125,230,4),(3930,455,3460,535,130,205,-5),(4410,450,3370,420,145,235,9),(4800,465,3240,160,115,155,-6),(5000,480,3150,20,35,45,0)]),
 ('near_low_return',[(2660,515,4310,25,35,50,0),(2980,535,4200,260,165,225,-12),(3390,540,4300,335,145,280,7),(3800,510,4370,280,165,195,-9),(4220,525,4310,300,185,235,12),(4640,530,4180,265,185,200,-7),(4930,510,4020,30,45,65,0)]),
 ('far_low_return',[(2740,490,3010,20,30,40,0),(3120,525,2910,275,170,190,8),(3530,530,2870,270,165,235,-12),(3960,505,2820,285,155,200,8),(4400,520,2670,255,175,195,-9),(4760,495,2740,130,115,150,4),(4920,485,2830,15,30,45,0)]),
 ('east_turned_belly',[(4560,450,3040,25,40,60,0),(4780,490,3360,220,170,225,12),(4800,540,3700,295,165,235,-13),(4640,550,4040,240,160,280,7),(4480,510,4300,30,45,65,0)]),
 ('near_unequal_crown_fold',[(2740,600,4050,20,35,45,0),(2950,690,3900,180,170,150,-13),(3210,725,3960,230,190,175,7),(3440,670,4100,190,135,160,11),(3600,575,4210,20,40,55,0)]),
 ('middle_forked_crown',[(3270,585,3140,20,35,45,0),(3510,685,3250,175,160,155,11),(3780,695,3410,205,180,195,-9),(4050,660,3390,180,145,160,14),(4330,575,3510,20,40,55,0)]),
 ('east_high_return_fold',[(4290,590,4230,20,35,45,0),(4550,680,4170,185,170,170,-14),(4740,710,4010,195,185,190,9),(4810,660,3800,145,100,170,-10),(4880,565,3650,20,30,50,0)]),
 ('far_small_stepped_fold',[(3690,565,2660,20,30,40,0),(3940,620,2720,140,120,130,8),(4170,665,2710,135,145,145,-12),(4380,610,2830,115,90,135,9),(4530,550,2880,15,25,40,0)]),
 ('west_side_curl',[(2610,440,3350,15,30,40,0),(2720,500,3570,155,125,155,18),(2700,570,3820,185,150,180,-13),(2880,580,4050,145,95,155,11),(3050,515,4160,20,30,45,0)]),
 # Two rare local angular lips, not a high cone on every ridge.
 ('near_offset_sharp_lip',[(3030,700,3910,12,25,30,0),(3130,815,3940,78,180,165,-16),(3230,740,3960,40,65,105,8),(3330,655,3980,10,20,25,0)]),
 ('far_single_break',[(4050,620,2660,10,20,25,0),(4130,720,2700,60,115,125,12),(4240,645,2740,35,55,80,-9),(4320,580,2780,10,20,25,0)]),
]


def catmull(a,b,c,d,t):
    return .5*((2*b)+(-a+c)*t+(2*a-5*b+4*c-d)*t*t+(-a+3*b-3*c+d)*t*t*t)


def closed_loft(name,knots):
    # Interpolated positions are a real 3D axis. Unequal upper and lower radii,
    # native roll and an asymmetric12-sided profile give side curls and bellies.
    sections=[]
    for k in range(len(knots)-1):
        a=knots[max(0,k-1)];b=knots[k];c=knots[k+1];d=knots[min(len(knots)-1,k+2)]
        distance=sqrt(sum((c[q]-b[q])**2 for q in range(3)))
        steps=max(2,round(distance/90))
        for s in range(steps):
            t=s/steps;row=[catmull(a[q],b[q],c[q],d[q],t) for q in range(7)]
            for q in (3,4,5):row[q]=max(6,row[q])
            sections.append(row)
    sections.append(list(knots[-1]));vertices=[];faces=[];rings=[]
    for k,p in enumerate(sections):
        prev=sections[max(0,k-1)];nxt=sections[min(len(sections)-1,k+1)]
        dx,dz=nxt[0]-prev[0],nxt[2]-prev[2];length=sqrt(dx*dx+dz*dz);nx,nz=-dz/length,dx/length
        roll=radians(p[6]);ring=[]
        # Authored axial asymmetry changes by section, never identical bulbs.
        for j,(side,vertical) in enumerate(PROFILE):
            lateral=side*p[3];height=vertical*(p[4] if vertical>=0 else p[5])
            lateral,height=lateral*cos(roll)-height*sin(roll),lateral*sin(roll)+height*cos(roll)
            ring.append(len(vertices));vertices.append((p[0]+nx*lateral,p[1]+height,p[2]+nz*lateral))
        rings.append(ring)
    for a,b in zip(rings,rings[1:]):
        for j in range(len(PROFILE)):
            n=(j+1)%len(PROFILE);faces.extend([(a[j],b[j],b[n]),(a[j],b[n],a[n])])
    for end,reverse in ((0,True),(-1,False)):
        ring=rings[end];p=sections[end];center=len(vertices);vertices.append(tuple(p[:3]))
        for j in range(len(PROFILE)):
            n=(j+1)%len(PROFILE);faces.append((center,ring[n],ring[j]) if reverse else (center,ring[j],ring[n]))
    return dict(name=name,knots=knots,vertices=vertices,faces=faces,section_count=len(sections),profile=PROFILE)


def controls():return [closed_loft(name,knots) for name,knots in LOFTS]
