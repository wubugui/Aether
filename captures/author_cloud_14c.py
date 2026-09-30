from pathlib import Path
root=Path('D:/test6'); p=root/'captures'
s=(p/'model_cloud_14b.py').read_text(encoding='utf-8').replace('14b','14c')
s=s.replace('if j not in (0, 4): y += math.sin(i * 3.41 + j * 2.26) * min(4.8, radius * .3)', 'if j not in (0, 4):\n            y += math.sin(i * 3.41 + j * 2.26) * min(4.8, radius * .3)\n            y = max(bottom + radius * .03, min(top - radius * .03, y))')
dest=p/'model_cloud_14c.py';assert not dest.exists();dest.write_text(s,encoding='utf-8')
preview=(p/'preview_cloud_14b.gd').read_text(encoding='utf-8').replace('14b','14c')
(p/'preview_cloud_14c.gd').write_text(preview,encoding='utf-8')
print('14c cloud profile control and altitude-layer material authored')
