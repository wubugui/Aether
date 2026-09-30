from pathlib import Path
R=Path(__file__).resolve().parents[1]
s=(R/'captures/localize_island_31b_back_cleft.py').read_text()
s=s.replace('lantern-island-31b-20260908T195540Z-dc0f57e0a037461484c11dba7dcb8b57','lantern-island-31d-20260908T201625Z-7575af2955e449b1a68d49f13e66c31a').replace('31b','31d')
s=s.replace('[[790,535],[785,570],[817,530],[811,565]]','[[760,505],[848,510],[711,549],[939,563],[804,538],[784,597]]')
s=s.replace('round-31d-back-cleft-localization.json','round-31d-rear-flank-localization.json')
s=s.replace('Targeted rays on two sides of visible31d day-d-back cleft.','Six targeted rays on directly viewed31d rear upper/lower flanks, new fill and seaward cleft end.')
s=s.replace('Four current rear-cleft sample surfaces localized for next authored break/width/depth changes.','Current31d rear flanks and inserted shoulder surfaces localized to design connected wider facet changes rather than repeatedly enlarge a narrow filler.')
exec(compile(s,str(__file__),'exec'))
