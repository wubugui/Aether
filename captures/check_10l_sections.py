from pathlib import Path
root=Path('D:/test6')
source=(root/'captures/check_section_surface_overlaps.py').read_text().replace('round-10a-section-overlap-check.json','round-10l-section-overlap-check.json')
exec(compile(source,'current source 10l section surfaces','exec'))
