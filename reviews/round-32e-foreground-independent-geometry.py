from pathlib import Path
src=(Path(__file__).parent/'round-32b-foreground-independent-geometry.py').read_text(encoding='utf-8-sig').replace('foreground_island_study_32b','foreground_island_study_32e').replace('round-32b-reopened-source','round-32e-reopened-source').replace('round-32b-foreground-independent-geometry','round-32e-foreground-independent-geometry').replace("'round':'32b'","'round':'32e'").replace('from32bdesign','from32edesign')
exec(compile(src,'32e_independent_actual_GLB_and_full_building_footprints','exec'))
