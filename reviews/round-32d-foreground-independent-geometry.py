from pathlib import Path
src=(Path(__file__).parent/'round-32b-foreground-independent-geometry.py').read_text(encoding='utf-8-sig').replace('foreground_island_study_32b','foreground_island_study_32d').replace('round-32b-reopened-source','round-32d-reopened-source').replace('round-32b-foreground-independent-geometry','round-32d-foreground-independent-geometry').replace("'round':'32b'","'round':'32d'").replace('from32bdesign','from32ddesign').replace('axis checks are','axis checks are')
exec(compile(src,'32d_independent_actual_GLB_and_full_building_footprints','exec'))
