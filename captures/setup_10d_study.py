from pathlib import Path
root=Path('D:/test6');out=root/'captures'
for name in ['cliff_sections_10c.py','verify_cliff_sections_10c.py','build_10c_ground.py','build_10c_study.py','preview_cliff_sections_10c.gd']:
    source=(out/name).read_text().replace('10c','10d')
    if name=='cliff_sections_10c.py':
        source=source.replace('p[1]=float(y-13*influence)', 'influence=max(influence,W.smooth(90,115,x)*(1-W.smooth(170,205,x))*W.smooth(-90,-40,z)*(1-W.smooth(60,110,z)))\n        p[1]=float(y-13*influence)')
        source=source.replace('foot[:,2]+=np.array([5,8,12,14,16,13,9,6])','foot[:,2]+=np.array([2,2,3,3,3,3,2,2])')
    (out/name.replace('10c','10d')).write_text(source)
