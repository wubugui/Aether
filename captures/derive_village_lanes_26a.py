from pathlib import Path
R=Path(__file__).resolve().parents[1]
old=(R/'tools/prepare_village_paving_24i.py').read_text()
prefix=old.split('groups=[]')[0].replace("village_paving_design_24i","village_paving_design_26a")
setup=old[old.index('for group in plan[\'groups\']:'):old.index('    dt=Delaunay(seed)')]
tail=(R/'tools/village_lanes_26a_body.py').read_text()
(R/'tools/prepare_village_paving_26a.py').write_text(prefix+'groups=[]\n'+setup+tail,encoding='utf-8')
