import sys
from PIL import Image, ImageDraw
out, d = sys.argv[1], sys.argv[2]; refs = sys.argv[3:]
w=500; h=int(w*941/1672.)
cols=4; rows=(len(refs)+1)//2
S=Image.new('RGB',(w*cols,h*rows),(20,20,20))
for i,r in enumerate(refs):
    c=(i%2)*2; row=i//2
    S.paste(Image.open('ref/%s.png'%r).convert('RGB').resize((w,h)),(c*w,row*h))
    try: S.paste(Image.open('%s/%s.png'%(d,r)).convert('RGB').resize((w,h)),((c+1)*w,row*h))
    except IOError: pass
    dr=ImageDraw.Draw(S); dr.rectangle([c*w,row*h,c*w+40,row*h+13],fill=(0,0,0)); dr.text((c*w+3,row*h+1),r,fill=(255,255,0))
S.save(out)
