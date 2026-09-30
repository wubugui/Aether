"""Grade actual route corridors while preserving building pads and native source pieces."""
from pathlib import Path
root=Path(__file__).resolve().parents[1]
target=root/'blender/model_lantern_islands_20j.py';assert not target.exists()
text=(root/'blender/model_lantern_islands_20i.py').read_text()
text=text.replace('lantern_islands_study_20i','lantern_islands_study_20j').replace("'label':'20i'","'label':'20j'")
text=text.replace("(.145,.127,.089)","(.085,.072,.046)")
start=text.index('    routes=([',text.index('# The route surface'))
end=text.index('    ribbons=[];width=',start)
routes=text[start:end]
routes=routes.replace('(-22,-9)','(-22,-8.15)').replace('(18.15,-11.63)','(18.2,-11.25)').replace('(-14.57,-8.34)','(-14.60,-8.03)').replace('(-12.7,-18.64)','(-12.66,-18.3)')
text=text[:start]+text[end:]
text=text.replace('    def height(x,y):','    def pad_height(x,y):',1)
start=text.index('    coords=[Vector(p) for p in boundary]')
grading='''    # Longitudinal profiles interpolate from actual entry platforms. Each branch
    # uses its already-graded junction height; first/last 2 m remain level.
    profiles=[]
    def closest_profile(point,profile):
        route,cumulative,z0,z1=profile;best=None
        for i in range(len(route)-1):
            a,b=Vector(route[i]),Vector(route[i+1]);edge=b-a
            t=max(0.,min(1.,(point-a).dot(edge)/edge.length_squared))
            d=(point-a-edge*t).length;s=cumulative[i]+edge.length*t
            progress=max(0.,min(1.,(s-2.)/max(1.,cumulative[-1]-4.)))
            value=z0+(z1-z0)*progress
            if best is None or d<best[0]:best=(d,value)
        return best
    for route in routes:
        cumulative=[0.]
        for a,b in zip(route,route[1:]):cumulative.append(cumulative[-1]+(Vector(b)-Vector(a)).length)
        ends=[]
        for p in [route[0],route[-1]]:
            value=pad_height(*p)
            for prior in profiles:
                distance,joined=closest_profile(Vector(p),prior)
                if distance<.05:value=joined
            ends.append(value)
        profiles.append((route,cumulative,*ends))
    def height(x,y):
        value=pad_height(x,y);point=Vector((x,y))
        distance,grade=min((closest_profile(point,p) for p in profiles),key=lambda pair:pair[0])
        # Level crossfall over the full path and shoulders, fading into terrain.
        if distance<5.:
            t=max(0.,min(1.,(distance-2.0)/3.0));weight=1-t*t*(3-2*t)
            value=value*(1-weight)+grade*weight
        # Protect each actual structure platform, with a short smooth outer join.
        for cx,cy,wx,wy,angle in pads:
            co,si=math.cos(angle),math.sin(angle);dx,dy=x-cx,y-cy
            u,v=co*dx+si*dy,-si*dx+co*dy
            d=max(abs(u)-wx,abs(v)-wy,0.)
            if d<1.2:
                t=d/1.2;weight=1-t*t*(3-2*t)
                value=value*(1-weight)+ungraded(cx,cy)*weight
        return value
'''
text=text[:start]+routes+grading+text[start:]
marker='    for cx,cy,wx,wy,angle in pads:\n        co,si=math.cos(angle),math.sin(angle)\n        for u,v in [(-wx,-wy)'
start=text.index(marker)
sampling='''    # Densely constrain only the narrow route corridor; the outer island keeps
    # broad facets. This captures real crossfall instead of bridging steep faces.
    for route in routes:
        for a,b in zip(route,route[1:]):
            a,b=Vector(a),Vector(b);edge=b-a;normal=Vector((-edge.y,edge.x)).normalized()
            steps=max(2,math.ceil(edge.length/1.2))
            for i in range(steps+1):
                center=a.lerp(b,i/steps)
                for offset in [-4.8,-2.05,-.95,0.,.95,2.05,4.8]:
                    p=center+normal*offset
                    if inside(p.x,p.y,boundary):coords.append(p)
'''
text=text[:start]+sampling+text[start:]
text=text.replace("Inclined and offset cliff fracture bands, raised exposed rock shoulders and actual terrain-fitted keeper routes.","Inclined cliff fracture bands and exposed rock shoulders with actual graded route corridors preserving structure platforms.")
text=text.replace('Three locally remodeled islands with terrain-fitted paths;','Three remodeled islands with graded terrain-fitted paths;')
target.write_text(text);print(target)
