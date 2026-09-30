from pathlib import Path
s=(Path(__file__).parent/'round-32b-reopen-native.py').read_text(encoding='utf-8-sig')
s=s.replace('foreground_island_study_32b','rightcoast_study_33a').replace("'island_a.blend'","'mainland_headland.blend'").replace('len(stats)==11','len(stats)==12').replace('round-32b-reopened-source','round-33a-reopened-source')
start=s.index('trees=[]');end=s.index('after=hashlib',start);s=s[:start]+'trees=[]\n'+s[end:]
s=s.replace('Independent actual saved32b source opened in fresh background Blender; no builder rerun or source save. Native mesh validity and8planned tree-axis top hits across all11meshes.','Independent actual33a saved source reopened once in fresh Blender; no builder rerun or source save.12native meshes; no tree/world test.')
exec(compile(s,'33a_independent_saved_source_reopen','exec'))
