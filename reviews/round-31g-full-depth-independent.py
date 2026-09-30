from pathlib import Path
src=(Path(__file__).parent/'round-31g-cut-patch-independent.py').read_text(encoding='utf-8')
src=src.replace("captures/island-31g-cut-patch.json","captures/island-31g-cut-patch-full-depth.json").replace("round-31g-cut-patch-independent.json","round-31g-full-depth-independent.json").replace("round-31g-cut-patch-independent.md","round-31g-full-depth-independent.md")
exec(compile(src,'31g_full_depth','exec'))
