from pathlib import Path
R=Path(__file__).resolve().parents[1]
s=(R/'tools/render_lantern_island_30k.py').read_text()
s=s.replace("ValidationRun(root,'lantern-island-30k',", "ValidationRun(root,'lantern-island-30k-r1',")
s=s.replace('"ground_collider":str(hit.collider.get_path())})', '"ground_collider":str(hit.collider.get_path()),"island_root":str(islands[island_name].get_path())})')
s=s.replace("island_name in actual['ground_collider']", "actual['ground_collider'].startswith(actual['island_root']+'/')")
p=R/'tools/render_lantern_island_30k_r1.py';assert not p.exists();p.write_text(s)
print('30k retry records actual runtime island root and checks collider ancestry')
