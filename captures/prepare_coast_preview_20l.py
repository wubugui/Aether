from pathlib import Path
root=Path(__file__).resolve().parents[1]
p=root/'captures/preview_lantern_islands_20.gd';s=p.read_text()
s=s.replace('label=="20k"','label in ["20k","20l"]')
s=s.replace('"20j","20k"]','"20j","20k","20l"]')
s=s.replace('"20i","20j"]','"20i","20j","20k","20l"]')
p.write_text(s)
