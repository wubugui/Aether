from pathlib import Path
R=Path(__file__).resolve().parents[1];s=(R/'tools/render_foreground_island_32b.py').read_text(encoding='utf-8').replace('32b','32d');p=R/'tools/render_foreground_island_32d.py';assert not p.exists();p.write_text(s,encoding='utf-8')
