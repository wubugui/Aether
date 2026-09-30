from pathlib import Path
R=Path(__file__).resolve().parents[1]
p=(R/'blender/model_coastal_sky_27b.py').read_text().replace("OUT=ROOT/'captures/coastal_sky_assets_27b'","OUT=ROOT/'captures/coastal_sky_assets_27c'")
p=p.replace('h*=1.35','h*=1.70')
p=p.replace('sections=[(-1.,.035),(-.72,.62),(-.34,.90),(.05,1.),(.40,.84),(.72,.57),(1.,.035)]','sections=[(-1.,.035),(-.75,.50),(-.35,.82),(-.10,1.),(.20,.78),(.55,.49),(1.,.035)]\n    ridge_heights=[.06,.32,.80,1.12,.65,.36,.06]')
p=p.replace('ridge=1.+.13*math.sin(j*1.7+turn*3.)','ridge=ridge_heights[j]')
p=p.replace('z=cz+h*(.05+.13*spread+math.sin(angle)*spread*(.84*ridge if math.sin(angle)>=0 else .43))','z=cz+h*(.03+.06*spread+math.sin(angle)*(ridge if math.sin(angle)>=0 else .32*spread))')
p=p.replace('New editable cloud lobes use seven shaped cross-sections and twelve radial samples with an asymmetric ridge and rounded underside;27a flat-hull cloud prototype retained separately.','27c cloud lobes use an explicit asymmetric pointed ridge, greater vertical depth and continuous rounded undersides.27a/b failed proportions preserved separately.')
(R/'blender/model_coastal_sky_27c.py').write_text(p,encoding='utf-8')
g=(R/'captures/check_coastal_sky_27b.py').read_text().replace('27b','27c');(R/'captures/check_coastal_sky_27c.py').write_text(g,encoding='utf-8')
