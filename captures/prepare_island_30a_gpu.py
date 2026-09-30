from pathlib import Path
R=Path(__file__).resolve().parents[1]
s=(R/'tools/render_lantern_island_29e.py').read_text().replace('29e','30a').replace("'terrain-plan.json'","'proportion-plan.json'")
marker="            cut=s.index(";at=s.index(marker)
injection='''            s=s.replace('var proposed:=Vector3(-2340,0,-1810)','var proposed:=Vector3(-2372,0,-1812)').replace('model("island_c",proposed,.55)','model("island_c",proposed,2.0)').replace('"yaw":.55','"yaw":2.0')
            needle='\\tvar at:Vector3=islands[island_name].to_global(offset)'
            replacement='\\tif island_name in ["island_c","island_d"]:\\n\\t\\toffset=Vector3(1.5,0,.8) if kind=="lighthouse" else offset*.72\\n'+needle
            require(needle in s,'Building placement insertion missing');s=s.replace(needle,replacement)
            s=s.replace('else (.7 if island_name=="island_b" else .5)','else (.7 if island_name=="island_b" else .36)')
'''
s=s[:at]+injection+s[at:]
s=s.replace("run.manifest.update(scope='C/D30a connected terrain and original bedrock topology remodeling, retaining occupied20l pad/tree support and rebuilding terrain-fitted road on broad graded shoulders,26b mainland and28h optics. Five actual views from two scene loads; preserve original structure/tree placements and footing samples. No production/whole-world generation.'","run.manifest.update(scope='C/D30a native land proportion and full-size occupied-site rebuild. Buildings/trees re-grounded; D position/orientation intentionally changed. Unaffected A/B, reefs, mainland and production remain. Fixed reference camera and five GPU views.'")
start=s.index('                    require(len(d[\'placements\'])');end=s.index('            run.assert_inputs()',start)
s=s[:start]+'''                    def affected(p):return p.get('island') in ['island_c','island_d'] or p['kind']=='island_c'
                    unchanged=[p for p in d['placements'] if not affected(p)];before=[p for p in old['placements'] if not affected(p)]
                    require(len(unchanged)==len(before),'Unchanged site count changed');maximum=0.
                    for a,b in zip(unchanged,before):
                        require(a['kind']==b['kind'] and a.get('island')==b.get('island'),'Unchanged placement identity changed')
                        maximum=max(maximum,max(abs(x-y) for x,y in zip(a['position'],b['position'])))
                    require(maximum<.001,'Unchanged region moved')
                    buildings=[p for p in d['placements'] if p.get('island') in ['island_c','island_d'] and p['kind'] in ['lighthouse','keeper_house']]
                    require(len(buildings)==4,'Expected two full-size tower and two keeper sites')
                    old_footing={p['building']:p for p in old['footing_samples']};rebuilt=[];unaffected_foundation_delta=0.
                    for f in d['footing_samples']:
                        center=f['samples'][4]['position'];matches=[p for p in buildings if abs(p['position'][0]-center[0])+abs(p['position'][2]-center[2])<.02]
                        if matches:
                            require(len(matches)==1,'Ambiguous rebuilt building');b=matches[0];expected=-.5 if b['kind']=='lighthouse' else -.65*.7
                            gaps=[p['gap_m'] for p in f['samples']];require(all(g is not None and abs(g-expected)<.10 for g in gaps),'New building support outside expected foundation embed: '+str(gaps))
                            require(abs(b['scale']-(1. if b['kind']=='lighthouse' else .7))<1e-6,'Native building scale changed')
                            rebuilt.append({'building':f['building'],'island':b['island'],'kind':b['kind'],'position':b['position'],'scale':b['scale'],'sample_gaps_m':gaps})
                        else:
                            base=old_footing[f['building']]
                            for p,q in zip(f['samples'],base['samples']):unaffected_foundation_delta=max(unaffected_foundation_delta,abs(p['gap_m']-q['gap_m']))
                    require(len(rebuilt)==4 and unaffected_foundation_delta<.001,'Rebuilt/unaffected foundations invalid')
                    points.append({'view':name,'placement_count':len(d['placements']),'unchanged_placement_count':len(unchanged),'unchanged_maximum_position_delta_m':maximum,'unaffected_foundation_delta_m':unaffected_foundation_delta,'rebuilt_buildings':rebuilt,'affected_placements':[p for p in d['placements'] if affected(p)],'island_c_glb_sha256':d['island_c_glb_sha256']})
            report=run.directory/'actual-site-rebuild.json';write_json(report,{'run_id':run.run_id,'passed':True,'views':points,'design':{'land_blender_scale':[.72,.72,.65],'d_position':[-2372,0,-1812],'d_yaw':2.0,'tower_offset':[1.5,0,.8],'native_building_scales':[1.,.7]},'scope':'Actual same-world re-grounded native buildings and trees. Four rebuilt building3x3 foundation samples, unaffected regions compared with28h. No all-surface contact, full walking/flight or visual acceptance claim.'});run.bind(report)
'''+s[end:]
p=R/'tools/render_lantern_island_30a.py';assert not p.exists();p.write_text(s);print(p)
