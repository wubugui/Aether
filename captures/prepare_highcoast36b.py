from pathlib import Path

R = Path(__file__).resolve().parents[1]
out = R / 'blender/sculpt_highcoast_36b.py'
assert not out.exists()
s = (R / 'blender/sculpt_highcoast_36a.py').read_text(encoding='utf-8').replace('36a', '36b')
a = s.index('RIDGES=[')
b = s.index('\ndef smooth', a)
s = s[:a] + '''RIDGES=[
    [[-2520,-2460,35,220],[-2330,-2670,72,280],[-2070,-2880,145,330],[-1770,-2920,110,330]],
    [[-3110,-3680,65,280],[-2800,-3830,140,340],[-2380,-3950,285,420],[-2110,-4100,210,340]],
    [[-2650,-4140,100,250],[-2380,-3950,285,380],[-2050,-3820,190,340],[-1850,-3630,105,310]],
    [[-1730,-3570,95,320],[-1520,-3740,265,380],[-1330,-3910,325,340],[-1160,-4110,160,260]],
    [[-2710,-2730,34,130],[-2520,-2820,65,210],[-2280,-2830,105,220]],
]
RIVER=[[-3090,-3190,110],[-2840,-3200,98],[-2640,-3130,78],[-2450,-3220,74],[-2240,-3310,66],[-2030,-3240,62],[-1840,-3370,52],[-1600,-3330,45],[-1390,-3210,26]]
# Authored irregular rock shoulders. Each ring has a broad grass cap, a short
# sloped rim, and a low apron. These are edits to the continuous native mesh.
SHELVES=[
    (46,[[-2660,-2470],[-2500,-2420],[-2350,-2510],[-2400,-2610],[-2540,-2670],[-2690,-2600]]),
    (62,[[-2890,-2760],[-2740,-2690],[-2550,-2760],[-2500,-2880],[-2690,-2960],[-2870,-2890]]),
    (32,[[-2930,-3030],[-2750,-2970],[-2650,-3030],[-2740,-3120],[-2900,-3100]]),
    (54,[[-3220,-3420],[-3090,-3330],[-2910,-3370],[-2900,-3500],[-3090,-3550],[-3250,-3510]]),
    (79,[[-3400,-3760],[-3250,-3620],[-3070,-3690],[-3000,-3840],[-3200,-3890],[-3390,-3880]]),
    (42,[[-2290,-3030],[-2100,-2970],[-1950,-3100],[-2040,-3180],[-2240,-3150]]),
    (58,[[-2530,-3460],[-2350,-3390],[-2190,-3470],[-2250,-3590],[-2440,-3620]]),
]
''' + s[b:]
a = s.index('def sculpt_height(')
b = s.index('\nrows=[]', a)
s = s[:a] + '''def ring_distance(ring,x,z):
    inside=np.zeros(x.shape,dtype=bool);best=np.full(x.shape,np.inf)
    for a,b in zip(ring,ring[1:]+ring[:1]):
        dx=b[0]-a[0];dz=b[1]-a[1]
        t=np.clip(((x-a[0])*dx+(z-a[1])*dz)/(dx*dx+dz*dz),0,1)
        best=np.minimum(best,np.hypot(x-a[0]-t*dx,z-a[1]-t*dz))
        if abs(dz)>1e-9:
            inside^=((a[1]>z)!=(b[1]>z)) & (x<(b[0]-a[0])*(z-a[1])/dz+a[0])
    return np.where(inside,best,-best)

def sculpt_height(x,z,old):
    coast=-1900.+(z+1500.)*(2300./3500.)
    inland=x-coast
    edge=smooth(-3750,-3540,x)*(1-smooth(-1120,-900,x))*smooth(-4400,-4210,z)*(1-smooth(-2360,-2150,z))
    target=np.full(x.shape,14.)
    for ridge in RIDGES:
        distance,(height,width),t=nearest_line(ridge,x,z)
        profile=np.maximum(0.,1.-distance/width)**1.45
        target=np.maximum(target,14.+height*profile)
    # Low headlands leave broad valley space before the more distant spines.
    for height,ring in SHELVES:
        d=ring_distance(ring,x,z)
        apron=10.+(height-10.)*smooth(-60.,18.,d)
        target=np.maximum(target,apron)
    # The river continues through a broad low apron instead of jumping from
    # water to a 238m uphill wall in its final 150m.
    distance,(halfwidth,),t=nearest_line(RIVER,x,z)
    bed=-5.+3.*t
    bank=bed+(6.-bed)*smooth(halfwidth*.66,halfwidth+28.,distance)
    bank+=18.*smooth(halfwidth+55.,halfwidth+150.,distance)
    blend=smooth(halfwidth+155.,halfwidth+370.,distance)
    carve=bank*(1-blend)+target*blend
    end_fade=1-smooth(.82,1.,t)
    target=np.where(distance<halfwidth+370.,target*(1-end_fade)+np.minimum(target,carve)*end_fade,target)
    target=old*(1-smooth(-15,36,inland))+target*smooth(-15,36,inland)
    return old*(1-edge)+target*edge,edge
''' + s[b:]
s = s.replace('grass=np.array([.40,.48,.285])', 'grass=np.array([.46,.54,.335])')
s = s.replace('rock=np.array([.44,.455,.45])', 'rock=np.array([.49,.51,.505])')
s = s.replace("tidal_estuary_controls=RIVER,", "tidal_estuary_controls=RIVER,shoulder_controls=SHELVES,")
s = s.replace('authored coastal spines and tidal estuary', 'lower rock shoulders, recessed spines and broad estuary apron')
out.write_text(s, encoding='utf-8')
print(out)
