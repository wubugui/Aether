from pathlib import Path
src=(Path(__file__).parent/'round-32b-foreground-independent-geometry.py').read_text(encoding='utf-8-sig').replace('foreground_island_study_32b','foreground_island_study_32f').replace('round-32b-reopened-source','round-32f-reopened-source').replace('round-32b-foreground-independent-geometry','round-32f-foreground-independent-geometry').replace("'round':'32b'","'round':'32f'").replace('from32bdesign','from32fdesign')
exec(compile(src,'32f_independent_GLB_and_full_affected_building_footprints','exec'))
