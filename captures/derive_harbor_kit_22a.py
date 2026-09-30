"""Write a standalone Blender builder using the established coastal authoring helpers."""
from pathlib import Path
root=Path(__file__).resolve().parents[1]
source=(root/'blender/model_lantern_islands_20h.py').read_text(encoding='utf-8')
prefix=source[:source.index('# Hand-shaped coast outline:')]
prefix=prefix.replace('lantern_islands_study_20h','harbor_kit_study_22a')
body=r'''
# Structural wood follows the existing keeper/lighthouse palette.
timber=[mat('Harbor oak plank '+str(i),c) for i,c in enumerate([(.135,.074,.035),(.175,.098,.046),(.21,.123,.059),(.155,.086,.041)])]
endgrain=mat('Harbor timber end grain',(.104,.056,.027))
rope_mat=mat('Harbor hemp lashings',(.24,.17,.09))
canvas=mat('Harbor weathered red canvas',(.235,.055,.030),rough=.95)
sailcloth=mat('Harbor flax sail',(.43,.37,.25),rough=.98)
lampglass=mat('Harbor lantern glass',(.25,.18,.07),rough=.22)
lampglass.node_tree.nodes.get('Principled BSDF').inputs['Alpha'].default_value=.34
lampglass.surface_render_method='DITHERED'
lampcore=mat('Harbor lantern flame',(.8,.33,.045))
lampcore.node_tree.nodes.get('Principled BSDF').inputs['Emission Color'].default_value=(1.,.38,.065,1)
lampcore.node_tree.nodes.get('Principled BSDF').inputs['Emission Strength'].default_value=.9

def cylinder(name,at,radius,depth,material,n=12):
    x,y,z=at
    rings=[[(x+radius*math.cos(i*math.tau/n),y+radius*math.sin(i*math.tau/n),z+h) for i in range(n)] for h in [-depth/2,depth/2]]
    return loft(name,rings,material)

def hoop(name,at,radius,width,material,n=16,thickness=.025):
    x,y,z=at;verts=[]
    for r,h in [(radius,-width/2),(radius,width/2),(radius-thickness,-width/2),(radius-thickness,width/2)]:
        verts.extend([(x+r*math.cos(i*math.tau/n),y+r*math.sin(i*math.tau/n),z+h) for i in range(n)])
    faces=[]
    for i in range(n):
        j=(i+1)%n
        faces.extend([(i,j,n+j,n+i),(2*n+i,3*n+i,3*n+j,2*n+j),(i,2*n+i,2*n+j,j),(n+i,n+j,3*n+j,3*n+i)])
    return mesh(name,verts,faces,material)

def cord(name,points,radius=.03):
    for i,(a,b) in enumerate(zip(points,points[1:])):beam(name+' span %02d'%i,a,b,radius*2,radius*2,rope_mat)

def pier(name,width,length):
    reset();deck=2.35;half=width/2
    # Every board is an editable, thick timber with two tiny nail heads.
    rows=math.ceil(length/.43);board_depth=length/rows
    for i in range(rows):
        y=-length/2+(i+.5)*board_depth
        box('Deck crossboard %02d'%i,(0,y,deck-.075),(width,board_depth-.018,.15),timber[i%4])
        for x in [-half+.32,half-.32]:cylinder('Recessed nail %02d %s'%(i,x),(x,y,deck+.002),.018,.012,metal,6)
    for x in [-half+.28,0,half-.28]:box('Long continuous stringer '+str(x),(x,0,deck-.31),(.20,length+.2,.30),timber[0])
    bays=math.ceil(length/3.6)
    for j in range(bays+1):
        y=-length/2+.28+j*(length-.56)/bays
        for side in [-1,1]:
            x=side*(half-.22)
            cylinder('Foundation pile %s %02d'%(side,j),(x,y,-1.30),.18,8.2,timber[(j+1)%4],8)
            cylinder('Pile end cap %s %02d'%(side,j),(x,y,2.83),.187,.09,endgrain,8)
            hoop('Iron pile band %s %02d'%(side,j),(x,y,2.54),.192,.14,metal,8)
        box('Pile crosshead %02d'%j,(0,y,deck-.53),(width+.3,.28,.24),timber[1])
        beam('Cross bent left %02d'%j,(-half+.22,y,-.8),(half-.22,y,1.6),.18,.19,timber[0])
    for side in [-1,1]:
        x=side*(half+.02)
        for j in range(3):
            y=length/2-1-j*2.0
            box('Rear guard post %s %s'%(side,j),(x,y,2.83),(.15,.15,1.13),timber[1])
        for j in range(2):
            a=length/2-1-j*2.;b=a-2.
            cord('Sagging hand rope %s %s'%(side,j),[(x,a,3.25),(x,(a+b)/2,3.05),(x,b,3.25)],.035)
    for x,y in [(-half+.35,-length/2+.8),(half-.35,-length/2+.8)]:
        cylinder('Mooring bollard',(x,y,2.66),.13,.65,metal,10)
        box('Bollard horn',(x,y,2.89),(.48,.12,.11),metal)
    freeze(name,'Detailed piled timber pier, thick separate deck planks, cross-braced piles, iron fasteners, guard ropes and mooring hardware. Deck2.35m, pile bottom-5.4m. Sea-bottom anchoring is not yet surveyed.')

pier('timber_pier',4.4,16.)
pier('pier_landing',10.8,6.)

reset()
# A genuinely open repair awning, like the reference dock, with a sagging canopy.
for x,y in [(-3,-2.4),(3,-2.4),(-3,2.4),(3,2.4)]:
    box('Awning upright',(x,y,1.8),(.24,.24,3.6),timber[1])
    for dz in [0,.1,.2]:hoop('Hemp post lashing',(x,y,3.15+dz),.18,.05,rope_mat,10,.035)
    beam('Upright angled knee',(x,y,2.45),(x+(.8 if x<0 else -.8),y,3.35),.13,.16,timber[0])
for y in [-2.4,2.4]:box('Awning cross lintel',(0,y,3.4),(6.55,.20,.20),timber[2])
for x in [-3,3]:box('Awning side lintel',(x,0,3.40),(.18,5.35,.18),timber[0])
verts=[];nx,ny=12,8
for layer in range(2):
    for j in range(ny+1):
        y=-2.68+5.36*j/ny
        for i in range(nx+1):
            x=-3.32+6.64*i/nx
            z=3.55-.70*math.sin(math.pi*i/nx)*math.sin(math.pi*j/ny)+.09*math.sin(i*.6+j*.9)*math.sin(math.pi*i/nx)
            verts.append((x,y,z-layer*.025))
n=(nx+1)*(ny+1);faces=[]
for j in range(ny):
    for i in range(nx):
        a=j*(nx+1)+i;b=a+1;c=b+nx+1;d=a+nx+1
        faces.extend([(a,b,c),(a,c,d),(a+n,c+n,b+n),(a+n,d+n,c+n)])
outline=list(range(nx+1))+[j*(nx+1)+nx for j in range(1,ny+1)]+[ny*(nx+1)+i for i in range(nx-1,-1,-1)]+[j*(nx+1) for j in range(ny-1,0,-1)]
for a,b in zip(outline,outline[1:]+outline[:1]):faces.append((a,a+n,b+n,b))
mesh('Thick tensioned red canvas',verts,faces,canvas)
for x in [-3,3]:
    for y in [-2.4,2.4]:cord('Corner tied canopy',[(x,y,3.6),(x*1.11,y*1.12,3.56),(x,y,2.95)],.027)
# Open-legged carpentry bench and practical scene tools.
for i in range(6):box('Workbench top board %d'%i,(-1.25+i*.49,.40,1.12),(.475,1.25,.13),timber[i%4])
for x in [-1.10,1.10]:
    for y in [-.1,.95]:box('Workbench leg',(x,y,.50),(.15,.15,1.0),timber[0])
    beam('Bench trestle brace',(x,-.1,.12),(x,.95,.9),.11,.13,timber[1])
box('Workbench lower tray',(0,.40,.34),(2.8,1.12,.10),timber[2])
box('Iron vise fixed jaw',(1.14,.0,1.29),(.28,.12,.30),metal)
box('Iron vise moving jaw',(1.14,-.23,1.29),(.28,.08,.30),metal)
beam('Vise threaded screw',(1.14,-.38,1.21),(1.14,.08,1.21),.055,.055,metal)
beam('Vise handle',(1.14,-.38,1.06),(1.14,-.38,1.43),.035,.035,metal)
beam('Carpenter hammer handle',(-.9,.0,1.215),(-.45,.32,1.215),.07,.07,timber[3])
box('Carpenter hammer iron head',(-.45,.32,1.24),(.26,.10,.09),metal,.6)
for i in range(3):box('Stored repair plank %d'%i,(-2.15+i*.22,1.5,.13+i*.06),(.23,1.9,.08),timber[i])
freeze('repair_awning','Open four-post wooden repair shelter with tensioned volumetric fabric, lashings, braces, plank workbench, vise and hammer. No reference HUD or characters.')

reset()
box('Lantern tall square post',(0,0,1.60),(.18,.18,3.2),timber[1])
box('Lantern post foot shoe',(0,0,.18),(.25,.25,.36),metal)
box('Lantern suspension arm',(.45,0,3.04),(1.1,.16,.18),timber[2])
beam('Lantern arm brace',(.06,0,2.40),(.85,0,2.98),.105,.11,timber[0])
cord('Lantern hanging link',[(.84,0,3.02),(.84,0,2.81)],.025)
cx,cy,cz=.84,0,2.44
box('Lantern bronze floor',(cx,cy,cz-.32),(.44,.44,.08),metal)
box('Lantern bronze cornice',(cx,cy,cz+.31),(.45,.45,.07),metal)
for x in [-.185,.185]:
    for y in [-.185,.185]:box('Lantern corner mullion',(cx+x,cy+y,cz),(.035,.035,.64),metal)
for side in [-1,1]:
    box('Lantern front rear glass',(cx,cy+side*.18,cz),(.34,.014,.58),lampglass)
    box('Lantern side glass',(cx+side*.18,cy,cz),(.014,.34,.58),lampglass)
loft('Lantern pyramidal cap',[[(cx+x,cy+y,cz+.35) for x,y in [(-.27,-.27),(.27,-.27),(.27,.27),(-.27,.27)]],[(cx+x,cy+y,cz+.54) for x,y in [(-.05,-.05),(.05,-.05),(.05,.05),(-.05,.05)]]],metal)
cylinder('Lantern glass flame',(cx,cy,cz),.055,.26,lampcore,10)
freeze('harbor_lantern','Timber gallows lantern with brace, iron foot, hollow cage, four thin glass panes, cap and actual warm core at local(.84,0,2.44). Runtime light uses the transformed core position.')

def barrel(name,x,y,z):
    for i in range(16):
        a=i*math.tau/16+.012;b=(i+1)*math.tau/16-.012;verts=[]
        for h,r in [(0,.44),(.58,.55),(1.15,.46)]:
            for rad,angle in [(r,a),(r,b),(r-.065,b),(r-.065,a)]:verts.append((x+rad*math.cos(angle),y+rad*math.sin(angle),z+h))
        faces=[(3,2,1,0),(8,9,10,11)]
        for j in range(2):
            for k in range(4):faces.append((j*4+k,j*4+(k+1)%4,(j+1)*4+(k+1)%4,(j+1)*4+k))
        mesh(name+' oak stave %02d'%i,verts,faces,timber[i%4])
    for h,r in [(.14,.478),(.43,.545),(.91,.508)]:hoop(name+' iron hoop',(x,y,z+h),r,.08,metal)
    cylinder(name+' closed wooden lid',(x,y,z+1.105),.418,.06,timber[2],16)
    beam(name+' lid batten',(x-.34,y,z+1.15),(x+.34,y,z+1.15),.07,.06,timber[0])
def crate(name,x,y,z):
    for i in range(4):
        v=-.405+i*.27
        for side in [-1,1]:
            box(name+' front back plank',(x+v,y+side*.50,z+.49),(.255,.085,.94),timber[i%4])
            box(name+' side plank',(x+side*.50,y+v,z+.49),(.085,.255,.94),timber[(i+1)%4])
        box(name+' lid board',(x+v,y,z+.98),(.255,1.05,.08),timber[(i+2)%4])
        box(name+' floor board',(x+v,y,z+.04),(.255,1.05,.08),timber[1])
    for side in [-1,1]:
        for xoff in [-.4,.4]:box(name+' strapping batten',(x+xoff,y+side*.55,z+.49),(.11,.10,1.06),timber[0])
        beam(name+' diagonal face brace',(x-.42,y+side*.61,z+.10),(x+.42,y+side*.61,z+.89),.11,.08,timber[2])
reset();barrel('Large dock barrel',-.85,0,0);barrel('Second dock barrel',.05,.95,0);crate('Cargo crate',.80,-.30,0);crate('Stacked crate',.82,-.29,1.02)
freeze('harbor_cargo','Two independent staved barrels with hoops/lids and two stacked board-built crates with diagonal braces.')

reset()
# Ten-point thick open hull cross-sections; interior is a real recess.
stations=[(-3.5,.035),(-2.7,.62),(-1.3,1.02),(.8,1.12),(2.6,.67),(3.6,.035)]
rings=[]
for y,w in stations:
    ztop=1.18+.27*(abs(y)/3.6)**2
    section=[(-w,ztop),(-w*.83,.30),(-w*.24,-.40),(w*.24,-.40),(w*.83,.30),(w,ztop),(w*.87,ztop-.04),(w*.69,.43),(0.,-.17),(-w*.69,.43),(-w*.87,ztop-.04)]
    rings.append([(x,y,z) for x,z in section])
hull=loft('Open planked fishing hull',rings,timber[1])
for side in [-1,1]:
    points=[(side*w,y,1.18+.27*(abs(y)/3.6)**2+.02) for y,w in stations]
    for j,(a,b) in enumerate(zip(points,points[1:])):beam('Continuous gunwale %s %s'%(side,j),a,b,.12,.12,timber[0])
    for fraction in [.25,.52,.78]:
        line=[(side*w*(.30+.70*fraction),y,-.35+fraction*1.54) for y,w in stations]
        for j,(a,b) in enumerate(zip(line,line[1:])):beam('Hull strake seam %s %s %s'%(side,fraction,j),a,b,.025,.025,endgrain)
for y,w in [(-1.9,.80),(.2,1.07),(1.65,.84)]:
    box('Crosswise seat thwart',(0,y,.94),(w*1.75,.40,.11),timber[2])
    for side in [-1,1]:beam('Interior bent rib',(side*w*.88,y,1.12),(side*.08,y,-.11),.085,.09,timber[0])
box('Boat interior sole',(0,0,-.06),(.68,3.45,.12),timber[3])
beam('Small fishing mast',(0,-.3,-.08),(0,-.3,6.15),.13,.14,timber[0])
beam('Lateen yard',(-.15,-2.60,2.20),(.05,2.1,5.7),.10,.11,timber[2])
beam('Boom',(0,-.30,1.5),(.0,2.7,1.5),.09,.10,timber[1])
# Thin canvas has real thickness and a bowed surface, not a scene background.
sv=[(-.03,-2.50,2.25),(.04,2.0,5.62),(.03,2.65,1.58),(.36,.60,2.84)]
sf=[(0,1,3),(1,2,3),(2,0,3)];verts=sv+[(x-.022,y,z) for x,y,z in sv]
faces=sf+[tuple(i+4 for i in reversed(t)) for t in sf]+[(0,4,5,1),(1,5,6,2),(2,6,4,0)]
mesh('Three-dimensional tensioned flax sail',verts,faces,sailcloth)
cord('Mast forward stay',[(0,-.30,6.05),(0,-3.3,1.47)],.025)
cord('Mast aft stay',[(0,-.30,6.05),(0,3.25,1.47)],.025)
cord('Sail sheet',[(.03,2.65,1.58),(.38,1.7,.76)],.023)
box('Stern rudder',(0,3.55,.20),(.10,.50,1.2),timber[0])
beam('Rudder tiller',(0,3.55,.83),(0,2.65,1.02),.07,.075,timber[2])
freeze('moored_fishing_boat','Static scene boat with an open thick hull, gunwales, internal ribs and seats, mast, bowed thick sail, rigging and rudder. No playable vehicle or characters; hull draft/water placement still needs scene inspection.')

(OUT/'model-report.json').write_text(json.dumps({'label':'22a','production_modified':False,'assets':reports,'scope':'Six detailed native harbor modules for the same coastal world. Independent Blender solids, no characters/UI. Not full scene acceptance.'},indent=2))
print('HARBOR KIT BUILT '+json.dumps({'assets':len(reports),'parts':sum(r['parts'] for r in reports)}),flush=True)
'''
target=root/'blender/model_harbor_kit_22a.py';assert not target.exists();target.write_text(prefix+body,encoding='utf-8');print(target)
