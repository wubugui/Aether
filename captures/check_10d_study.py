from pathlib import Path
root=Path('D:/test6')
source=(root/'captures/check_section_surface_overlaps.py').read_text()
source=source.replace("path=root/'assets/models'/('cliff_'+kind+'.glb')", "path=root/'captures'/('cliff_sections_10d_'+('prototype' if kind=='front_columns' else kind)+'.glb')")
source=source.replace('round-10a-section-overlap-check.json','round-10d-study-section-overlap.json')
exec(compile(source,'10d actual exported surface check','exec'))
