from pathlib import Path
root=Path(__file__).resolve().parents[1]
code=(root/'captures/village_paving_runtime_24l.gd').read_text(encoding='utf-8').replace('24l','24n')
code=code.replace('grading.paving_design_sha256==FileAccess.get_sha256(folder.path_join("village-paving/paving-design.json"))','grading.paving_design_sha256==design.source_24j_design_sha256')
code=code.replace('"ground_clearance_m":clearance','"ground_clearance_m":clearance,"ground_collider":str(ground.collider.get_path()),"paving_collider":str(hit.collider.get_path())')
(root/'captures/village_paving_runtime_24n.gd').write_text(code,encoding='utf-8')
code=(root/'tools/render_village_paving_24l.py').read_text(encoding='utf-8')
code=code.replace('village_paving_runtime_24l','village_paving_runtime_24n').replace("'village-paving-24l'","'village-paving-24n'")
code=code.replace('village_paving_study_24j','village_paving_study_24m').replace('round-24j-village-paving-native','round-24m-village-paving-native')
anchor="            graded=read_json(grading/'build-report.json');gcheck=read_json(grading_gate)"
extra="""
            original_design=read_json(root/'captures/village_paving_study_24j/paving-design.json')
            current_design=read_json(source/'paving-design.json')
            require(sha256(root/'captures/village_paving_study_24j/paving-design.json')==graded['paving_design_sha256'],'Original grading basis changed')
            for old,new in zip(original_design['groups'],current_design['groups']):
                require([s for s in old['solids'] if s['kind']=='foundation']==[s for s in new['solids'] if s['kind']=='foundation'],'Bedding changed beneath retained24l grading')
"""
assert anchor in code;code=code.replace(anchor,anchor+extra)
(root/'tools/render_village_paving_24n.py').write_text(code,encoding='utf-8')
