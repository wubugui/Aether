# Distinct native houses, real openings, deep eaves and individual thick roof shingles.
for name,width,depth,eave,ridge in [('fisher_cottage',5.5,7.6,3.3,5.65),('quay_workshop',8.2,6.2,3.5,5.25)]:
    reset();workshop=name=='quay_workshop';half=width/2;front=-depth/2
    box(name+' rubble footing',(0,0,-.15),(width+.6,depth+.6,1.),stone)
    box(name+' oak raised floor',(0,0,.42),(width,depth,.26),wood)
    door=1.35 if workshop else .7
    opening=[(-door,door,.5,2.9 if workshop else 2.6,'door')]
    if workshop:opening += [(-3.55,-2.35,1.4,2.75,'window'),(2.35,3.55,1.4,2.75,'window')]
    else:opening += [(1.3,2.3,1.35,2.6,'window'),(-2.3,-1.3,1.35,2.6,'window')]
    wall(name+' front',(0,front,0),(1,0,0),(0,-1,0),width,eave,opening)
    wall(name+' rear',(0,-front,0),(-1,0,0),(0,1,0),width,eave,[(-1.6,-.4,1.4,2.65,'window'),(.4,1.6,1.4,2.65,'window')])
    for side in [-1,1]:
        wall(name+' side '+str(side),(side*half,0,0),(0,side,0),(side,0,0),depth,eave,[(-2.3,-1.1,1.4,2.6,'window'),(1.1,2.3,1.4,2.6,'window')])
    for y in [front,-front]:
        loft(name+' masonry gable',[[(-half,y-.22,eave),(half,y-.22,eave),(0,y-.22,ridge-.13)],[(-half,y+.22,eave),(half,y+.22,eave),(0,y+.22,ridge-.13)]],plaster)
        beam(name+' verge',(-half-.3,y,eave-.03),(0,y,ridge),.15,.17,wood)
        beam(name+' verge',(0,y,ridge),(half+.3,y,eave-.03),.15,.17,wood)
    covering=roof if workshop else mat('Fisher muted russet shingles',(.19,.085,.055))
    span=half+.38;length=depth+.85;rows=6;pitch=.73
    for side in [-1,1]:
        for row in range(rows):
            a,b=row/rows,min(1,(row+1)/rows+.009);bias=(rows-row)*.018
            x0,x1=side*span*a,side*span*b;z0,z1=ridge-(ridge-eave)*a+bias,ridge-(ridge-eave)*b+bias
            for col in range(-1,math.ceil(length/pitch)+1):
                offset=.365 if row%2 else 0;ya=max(-length/2,-length/2+col*pitch+offset+.006);yb=min(length/2,-length/2+(col+1)*pitch+offset-.006)
                if yb-ya<.1:continue
                loft(name+' separate thick roof tile', [[(x0,ya,z0-.09),(x1,ya,z1-.09),(x1,yb,z1-.09),(x0,yb,z0-.09)],[(x0,ya,z0),(x1,ya,z1),(x1,yb,z1),(x0,yb,z0)]],covering)
        beam(name+' eaves fascia',(side*span,-length/2,eave),(side*span,length/2,eave),.18,.20,wood)
    for i in range(math.ceil(length/.8)):
        ya=-length/2+i*.8;yb=min(length/2,ya+.79)
        cross=[(-.16,ridge+.10),(.16,ridge+.10),(.15,ridge+.2),(0,ridge+.31),(-.15,ridge+.2)]
        loft(name+' ridge coping', [[(x,ya,z) for x,z in cross],[(x,yb,z) for x,z in cross]],covering)
    for x in [-half,half]:
        for y in [front,-front]:
            for i in range(5):box(name+' corner masonry quoin',(x,y,.8+i*.5),(.48,.48,.28),stone)
    for i,(distance,height) in enumerate([(1.15,.18),(.62,.35)]):box(name+' entry step '+str(i),(0,front-distance/2,height/2),(door*2+.3,distance,height),stone)
    canopy_width=3.25 if workshop else 2.5
    for x in [-canopy_width/2+.12,canopy_width/2-.12]:
        beam(name+' porch post',(x,front-1.28,0),(x,front-1.28,2.8),.16,.16,wood)
        beam(name+' canopy brace',(x,front-1.28,2.2),(x,front-.7,3.0),.12,.13,wood)
    loft(name+' thick canopy',[[(-canopy_width/2,front-1.42,2.8),(canopy_width/2,front-1.42,2.8),(canopy_width/2,front-.05,3.25),(-canopy_width/2,front-.05,3.25)],[(-canopy_width/2,front-1.42,2.95),(canopy_width/2,front-1.42,2.95),(canopy_width/2,front-.05,3.40),(-canopy_width/2,front-.05,3.40)]],covering)
    if workshop:
        for x in [-3.,3.]:
            box('Workshop front shutter',(x,front-.30,2.08),(1.13,.09,1.29),wood)
            for j in range(4):box('Workshop shutter board',(x-.44+j*.29,front-.37,2.08),(.25,.06,1.20),wood)
        beam('Workshop lifting beam',(0,front+.5,3.20),(0,front-1.55,3.20),.24,.24,wood)
    else:
        box('Fisher chimney masonry',(1.4,1.5,5.1),(.74,.80,2.1),stone)
        box('Fisher chimney cap',(1.4,1.5,6.22),(.94,1.,.16),stone)
        box('Fisher recessed chimney opening',(1.4,1.5,6.31),(.51,.55,.04),dark)
        # External racks are solid wood joinery, with separate crossed drying rails.
        for y in [-1.5,1.5]:beam('Fisher side rack post',(-half-.45,y,.0),(-half-.45,y,2.3),.12,.12,wood)
        for z in [.65,1.35,2.10]:beam('Fisher drying rail',(-half-.45,-1.5,z),(-half-.45,1.5,z),.09,.10,wood)
    freeze(name,'Independent editable '+name+' with real cut openings, thick separate roofing, entrance joinery, foundation and distinguishing fishing/workshop details; no furnished interior or scene acceptance.')
(OUT/'model-report.json').write_text(json.dumps({'label':'23d','production_modified':False,'assets':reports,'layout_sha256':survey['layout_sha256'],'survey_run':survey['run_id']},indent=2))
print('HEADLAND KIT BUILT '+str(len(reports))+' ASSETS',flush=True)
