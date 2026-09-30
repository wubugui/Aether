from pathlib import Path
root=Path(__file__).resolve().parents[1]
code=(root/'captures/village_paving_runtime_24n.gd').read_text(encoding='utf-8').replace('24n','25b')
code=code.replace('grading.paving_design_sha256==design.source_24j_design_sha256','grading.paving_design_sha256==FileAccess.get_sha256(folder.path_join("village-paving/paving-design.json"))')
(root/'captures/village_paving_runtime_25b.gd').write_text(code,encoding='utf-8')
code=(root/'tools/render_village_paving_24n.py').read_text(encoding='utf-8').replace('24n','25b').replace('24l','25b')
start=code.index('            original_design=read_json(');end=code.index("            require(graded['passed']",start)
code=code[:start]+"            require(sha256(source/'paving-design.json')==graded['paving_design_sha256'],'Earthworks/paving basis changed')\n"+code[end:]
anchor="                require(all(p['bottom_ground_gap_m']<.01 for p in village['foundation_samples']),'Paving foundation gap')"
extra="\n                require(all(abs(p['gap_m']+.65)<.002 for house in data['headland_study']['footings'] for p in house['samples']),'Original house foundation sample changed during earth fill')"
assert anchor in code;code=code.replace(anchor,anchor+extra)
code=code.replace('locally graded actual terrain','cut-and-fill actual village earthworks')
(root/'tools/render_village_paving_25b.py').write_text(code,encoding='utf-8')
