import sys
from PIL import Image, ImageDraw
# usage: sheet.py out.png cols w label=path ...
out=sys.argv[1]; cols=int(sys.argv[2]); w=int(sys.argv[3])
items=[a.split('=',1) for a in sys.argv[4:]]
ims=[]
for lab,p in items:
    im=Image.open(p).convert('RGB'); h=int(im.size[1]*w/float(im.size[0])); im=im.resize((w,h),Image.LANCZOS)
    d=ImageDraw.Draw(im); d.rectangle([0,0,8*len(lab)+8,16],fill=(0,0,0)); d.text((4,2),lab,fill=(255,255,0)); ims.append(im)
h=ims[0].size[1]; rows=(len(ims)+cols-1)//cols
sheet=Image.new('RGB',(cols*w,rows*h),(40,40,40))
for i,im in enumerate(ims): sheet.paste(im,((i%cols)*w,(i//cols)*h))
sheet.save(out)
