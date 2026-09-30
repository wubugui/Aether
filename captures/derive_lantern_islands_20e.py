"""Create distinct coastal silhouettes and actual inlets, retaining prior evidence."""
from pathlib import Path
root=Path(__file__).resolve().parents[1]
target=root/'blender/model_lantern_islands_20e.py'
assert not target.exists()
text=(root/'blender/model_lantern_islands_20d.py').read_text()
text=text.replace("lantern_islands_study_20d","lantern_islands_study_20e").replace("'label':'20d'","'label':'20e'")
start=text.index('    reset();coast=[]',text.index('def island('))
end=text.index('    # Only small building pads',start)
text=text[:start]+'''    reset()
    # Explicit independent coastlines: a cut eastern inlet, a bent western bay,
    # and a narrow hooked northern island. These are designed geography.
    outlines=[
        [(-90,-35),(-80,-60),(-45,-70),(-14,-56),(8,-48),(28,-60),(48,-53),(75,-46),(86,-22),(61,-17),(36,-12),(30,-3),(40,3),(69,4),(95,19),(83,40),(61,52),(34,61),(7,52),(-12,64),(-40,54),(-62,35),(-78,16),(-88,-4)],
        [(-84,-45),(-57,-68),(-24,-61),(2,-48),(33,-53),(62,-38),(70,-12),(52,9),(61,36),(38,63),(3,74),(-22,57),(-29,30),(-18,17),(-28,5),(-50,9),(-65,29),(-79,19),(-70,-8)],
        [(-58,-62),(-30,-73),(-4,-54),(25,-44),(51,-19),(45,1),(65,23),(49,43),(21,48),(10,67),(-12,73),(-27,49),(-11,28),(-4,15),(-19,8),(-48,26),(-66,10),(-74,-18)]
    ]
    coast=[(x*sx,y*sy) for x,y in outlines[variant]];count=len(coast)
    # Preserve concave mouth vertices rather than closing them with a radial cap.
    top_scales=[.93 if variant==0 and i in range(8,15) else (.94 if i%5 in (0,1) else .86) for i in range(count)]
    boundary=[(x*top_scales[i],y*top_scales[i]) for i,(x,y) in enumerate(coast)]
    def ungraded(x,y):
        a,b=x/sx,y/sy
        if variant==0:
            return max(3.1,plateau+7.*math.exp(-((a+1)/19)**2-((b-8)/23)**2)-.0018*a*a-.002*b*b+.12*a-.06*b)
        if variant==1:
            return max(3.4,plateau+6.*math.exp(-((a-8)/24)**2-((b-20)/25)**2)-.0022*a*a-.0015*b*b+.09*b)
        return max(2.8,plateau+5.*math.exp(-((a+6)/18)**2-((b-5)/28)**2)-.0015*a*a-.0018*b*b-.055*a)
'''+text[end:]
text=text.replace('u,v=co*dx-si*dy,si*dx+co*dy','u,v=co*dx+si*dy,-si*dx+co*dy')
text=text.replace('x,y=cx+co*u+si*v,cy-si*u+co*v','x,y=cx+co*u-si*v,cy+si*u+co*v')
text=text.replace('(9,-4,3.2,5.3,-.15)','(15,-15,3.2,5.3,-.15)')
text=text.replace('coords[:18]','coords[:count]').replace('[list(range(18))]','[list(range(count))]')
text=text.replace('k=top_scales[(i+variant*3)%18]','k=top_scales[i]')
text=text.replace('if source<18:index[source]=54+i','if source<count:index[source]=3*count+i')
text=text.replace('assert len(index)==18','assert len(index)==count').replace('range(18)','range(count)')
text=text.replace('j=(i+1)%18;a=level*18+i;b=level*18+j','j=(i+1)%count;a=level*count+i;b=level*count+j')
text=text.replace('(level+1)*18','(level+1)*count').replace('tuple(54+i for i in tri)','tuple(3*count+i for i in tri)')
start=text.index('    # Four unequal promontories')
end=text.index("    freeze(name,'Sculpted",start)
text=text[:start]+'''    # Three distinct outcrops belong to the high eastern cliff, leaving the west
    # low shore and the actual concave inlet unobstructed.
    headlands=([
        ((66,-37,0),(13,16,20),-.45),((76,33,0),(12,17,24),.2),((27,48,0),(22,10,14),-.35)] if variant==0 else
        ([((45,45,0),(17,12,20),.6),((57,-27,0),(9,20,13),-.4)] if variant==1 else
         [((-50,-36,0),(10,18,15),.3),((40,31,0),(17,10,11),-.6)]))
    for i,(pos,size,turn) in enumerate(headlands):
        x,y,z=pos;a,b,c=size
        block(name+' cliff outcrop %02d'%i,(x*sx,y*sy,z),(a*sx,b*sy,c*plateau/24),turn)
    shelves=([(-86,-45,13,8,3.5),(-67,-66,15,10,4),(11,-55,15,7,4),(91,34,10,9,6),(-60,40,10,12,3)] if variant==0 else
             ([(-66,-55,10,9,4),(61,-28,10,13,5),(35,65,11,9,5),(-78,19,8,11,4)] if variant==1 else
              [(-62,-49,10,8,4),(42,-27,10,8,4),(49,40,13,8,5),(-22,62,9,8,4)]))
    for i,(x,y,a,b,h) in enumerate(shelves):
        block(name+' low shore ledge %02d'%i,(x*sx,y*sy,-.5),(a*sx,b*sy,h),i*.43)
'''+text[end:]
text=text.replace('Sculpted constrained terrain with small graded building pads, unequal grass tongues and connected faulted rock cliffs.','Distinct concave coastline with an actual open inlet, asymmetric high cliff and low shore, locally graded building pads and sculpted slopes.')
start=text.index("for name,scale in [('reef_low'")
end=text.index('# Keeper architecture',start)
text=text[:start]+'''# Each offshore form has its own authored profile and silhouette.
reset()
loft('Low reef broad sloping slab',[
    [(-17,-7,-5),(2,-10,-5),(17,-5,-5),(14,7,-5),(-10,9,-5)],
    [(-16,-6,1),(2,-9,1),(16,-4,1),(13,6,1),(-9,8,1)],
    [(-11,-4,3),(3,-5,6),(11,-1,5),(8,3,3),(-7,5,2)]],rock)
block('Low reef separate shelf',(12,5,-1),(8,5,3),.5)
freeze('reef_low','Broad low slab with a tilted upper bedding plane and separate tidal shelf.')
reset()
loft('Spire leaning broken pinnacle',[
    [(-11,-8,-6),(7,-9,-6),(12,2,-6),(3,10,-6),(-9,6,-6)],
    [(-10,-7,1),(7,-8,1),(11,2,1),(3,9,1),(-8,6,1)],
    [(-6,-4,15),(4,-5,18),(6,2,17),(0,5,14),(-5,3,13)],
    [(-7,-1,22),(-2,-2,28),(0,1,26),(-3,3,20),(-6,2,21)]],rock)
block('Spire detached broken tooth',(8,4,-1),(5,7,11),-.3)
freeze('reef_spire','Leaning five-sided fractured sea pinnacle with a broken upper edge and lower tooth.')
reset()
loft('Ridge long oblique fin',[
    [(-28,-7,-5),(-8,-11,-5),(21,-6,-5),(29,1,-5),(8,9,-5),(-20,6,-5)],
    [(-27,-6,1),(-8,-10,1),(20,-5,1),(27,1,1),(8,8,1),(-19,5,1)],
    [(-20,-2,5),(-6,-5,13),(14,-2,17),(20,0,11),(5,3,8),(-16,2,4)]],rock)
block('Ridge lower fractured tail',(-24,1,-1),(9,6,5),-.2)
freeze('reef_ridge','Long tilted ridge with unequal peaks and a lower fractured tail, independently modeled from the spire and flat reef.')

'''+text[end:]
target.write_text(text)
print(target)
