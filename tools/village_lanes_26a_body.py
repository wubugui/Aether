    # Continuous laid-stone lanes replace the repeated rounded contour steps.
    # Keep the previously authored route plan, fixed door aprons and courtyard.
    from shapely.ops import polygonize
    from scipy.optimize import linprog
    from scipy.sparse import coo_matrix
    domain=shapely.set_precision(footprint,.001)
    lines2=[domain.boundary]+[shapely.set_precision(p['polygon'],.001).boundary for p in patches]
    for x in range(math.floor(minx),math.ceil(maxx)+1):
        q=LineString([(x,minz-1),(x,maxz+1)]).intersection(domain)
        if not q.is_empty:lines2.append(q)
    for z in range(math.floor(minz),math.ceil(maxz)+1):
        q=LineString([(minx-1,z),(maxx+1,z)]).intersection(domain)
        if not q.is_empty:lines2.append(q)
    cells=list(polygonize(shapely.union_all(lines2,grid_size=.001)))
    fv=[];ft=[];lookup={}
    def idx(p):
        key=tuple(round(v,3) for v in p)
        if key not in lookup:lookup[key]=len(fv);fv.append(key)
        return lookup[key]
    for cell in cells:
        if not domain.covers(cell.representative_point()):continue
        for tri in shapely.constrained_delaunay_triangles(cell).geoms:
            if tri.area>1e-10:ft.append([idx(p) for p in list(tri.exterior.coords)[:-1]])
    fv=np.array(fv);n=len(fv);preferred=np.array([field(x,z) for x,z in fv]);weight=np.zeros(n)
    rr=[];cc=[];values=[];rhs=[]
    def add(ids,coeff,b):
        rr.extend([len(rhs)]*len(ids));cc.extend(ids);values.extend(coeff);rhs.append(float(b))
    for ids in ft:
        v=fv[ids];inv=np.linalg.inv(v[1:]-v[0]);grad=np.column_stack([-inv.sum(axis=1),inv])
        weight[ids]+=Polygon(v).area/3
        for axis in range(2):add(ids,grad[axis],.30);add(ids,-grad[axis],.30)
    bounds=[];fixed_count=0
    for i,(x,z) in enumerate(fv):
        fixed=[p['height'] for p in patches if shapely.set_precision(p['polygon'],.001).buffer(.00001).covers(Point(x,z))]
        if fixed:
            assert max(fixed)-min(fixed)<.001;bounds.append((fixed[0],fixed[0]));fixed_count+=1
        else:bounds.append((min(p['height'] for p in patches),max(p['height'] for p in patches)))
        add([i,n+i],[1,-1],preferred[i]);add([i,n+i],[-1,-1],-preferred[i])
    matrix=coo_matrix((values,(rr,cc)),shape=(len(rhs),2*n)).tocsr()
    result=linprog(np.r_[np.zeros(n),weight],A_ub=matrix,b_ub=np.array(rhs),bounds=bounds+[(0,None)]*n,method='highs')
    assert result.success,(name,result.message)
    heights=result.x[:n];field_polys=[Polygon(fv[ids]) for ids in ft];field_tree=shapely.STRtree(field_polys)
    field_planes=[]
    for ids in ft:
        v=fv[ids]-np.array(hub);field_planes.append(np.linalg.solve(np.column_stack([v,np.ones(3)]),heights[ids]))
    def surface_y(p):
        at=Point(p);near=field_tree.query(at.buffer(.0011));inside=[j for j in near if field_polys[j].distance(at)<.0011]
        assert inside,('Lane field missing',p)
        j=min(inside,key=lambda j:field_polys[j].distance(at));return float((np.array(p)-hub)@field_planes[j][:2]+field_planes[j][2])
    def lane_solid(poly,kind,material,label):
        poly=shapely.set_precision(poly,.001)
        points=[];top_heights=[];lookup2={};faces=[]
        def vertex(p):
            key=tuple(round(v,5) for v in p)
            if key not in lookup2:lookup2[key]=len(points);points.append(key);top_heights.append(surface_y(key)-(0.012 if kind=='foundation' else 0))
            return lookup2[key]
        for j in field_tree.query(poly):
            cut=poly.intersection(field_polys[j])
            for piece in pieces(cut):
                if piece.area<1e-10:continue
                for tri in shapely.constrained_delaunay_triangles(piece).geoms:
                    if tri.area<1e-10:continue
                    ids=[vertex(p) for p in list(tri.exterior.coords)[:-1]]
                    if len(set(ids))==3:faces.append(ids)
        counts=defaultdict(int)
        for face in faces:
            for a,b in zip(face,face[1:]+face[:1]):counts[tuple(sorted((a,b)))]+=1
        assert all(count<=2 for count in counts.values()),('Nonmanifold lane cap',label)
        edges=[e for e,count in counts.items() if count==1]
        degree=defaultdict(int)
        for a,b in edges:degree[a]+=1;degree[b]+=1
        assert all(c==2 for c in degree.values()),('Pinched lane boundary',label)
        if kind=='foundation':
            bottom=min(min(top_heights),min(ground(x,z) for x,z in points))-2.8
            bottom_heights=[bottom]*len(points)
        else:bottom_heights=[h-.10 for h in top_heights]
        return {'name':label,'kind':kind,'material':material,'vertices_xz':points,'cap_triangles':faces,'boundary_edges':edges,'top_y':float(np.mean(top_heights)),'bottom_y':min(bottom_heights),'top_heights':top_heights,'bottom_heights':bottom_heights,'area_m2':poly.area}
    solids=[]
    # Editable local bedding blocks, capped by the same continuous lane field.
    for z in range(math.floor(minz/4),math.ceil(maxz/4)):
        for x in range(math.floor(minx/4),math.ceil(maxx/4)):
            tile=Polygon([(x*4,z*4),(x*4+4,z*4),(x*4+4,z*4+4),(x*4,z*4+4)])
            for i,p in enumerate(pieces(domain.intersection(tile))):
                if p.area>.002:solids.append(lane_solid(p,'foundation',0,name+' continuous buried bedding '+str((x,z,i))))
    angle=-20 if name=='foreground' else -10
    bx,bz,ex,ez=affinity.rotate(domain,-angle,origin=hub).bounds
    for row in range(math.floor(bz/.55),math.ceil(ez/.55)):
        offset=.4*(row%2)
        for col in range(math.floor((bx-offset)/.8),math.ceil((ex-offset)/.8)):
            x=col*.8+offset;z=row*.55
            tile=affinity.rotate(Polygon([(x+.004,z+.004),(x+.796,z+.004),(x+.796,z+.546),(x+.004,z+.546)]),angle,origin=hub)
            for i,p in enumerate(pieces(domain.intersection(tile))):
                if p.area>.022:solids.append(lane_solid(p,'paver',1+(row+col)%4,name+' inclined limestone '+str((row,col,i))))
    grading_faces=[{'vertices_xz':fv[ids].tolist(),'heights':heights[ids].tolist()} for ids in ft]
    groups.append({'name':name,'origin':[-2180,0,-1830],'footprint_geojson':shapely.to_geojson(domain),'grading_surface_triangles':grading_faces,'solids':solids,'fixed_patches':[{'house':p['house'],'height':p['height'],'geojson':shapely.to_geojson(p['polygon'])} for p in patches],'field_solve':{'vertices':n,'triangles':len(ft),'fixed_vertices':fixed_count,'success':True,'max_axis_slope':.30,'maximum_preferred_height_adjustment':float(np.max(abs(heights-preferred)))}})
    print(name,len(solids),'editable continuous lane solids; field',len(ft),'triangles',flush=True)
report={'label':'26a','headland_glb_sha256':plan['headland_glb_sha256'],'source_grid_run':plan['source_run'],'groups':groups,'scope':'Continuous inclined stone lanes with shared planar height field, fixed door aprons/courtyards and individually editable stones. Replaces scalloped quantized contours. Requires updated actual terrain grading, native source/export checks and GPU review before acceptance. Production unchanged.'}
(out/'paving.json').write_text(json.dumps(report,indent=2),encoding='utf-8')
