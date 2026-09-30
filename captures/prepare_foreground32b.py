from pathlib import Path
R=Path(__file__).resolve().parents[1]
s=(R/'blender/model_foreground_island_32a.py').read_text(encoding='utf-8').replace('32a','32b')
s=s.replace("# Full native house footprints", "# Full native house footprints")
s=s.replace("routes=[[", "pads.append(dict(id='tower',xy=[-3,6],half=[4.25,4.25],yaw=.25,height=30.0621032714844,scale=1.))\nroutes=[[")
s=s.replace("x,y,z=v.co;delta=0.","x,y,z=v.co;delta=0.;full_pad_delta=None;weights=[]")
s=s.replace("delta+=(pad['height']-oldheight(sx,sy))*weight", "change=pad['height']-oldheight(sx,sy)\n     weights.append((change,weight))\n     if distance<1e-5:full_pad_delta=change")
s=s.replace("v.co.z+=delta*min", "if full_pad_delta is not None:delta=full_pad_delta\n   elif weights:delta=sum(d*w for d,w in weights)/max(1.,sum(w for d,w in weights))\n   v.co.z+=delta*min")
s=s.replace("for pad in pads+[dict(id='tower',xy=[-3,6],half=[4.015,4.015],yaw=.25,height=30.0621032714844)]:", "for pad in pads:")
s=s.replace("Existing tower and all other world regions retained.","Tower position is retained and its complete terrain pad is protected explicitly.32a failed because the new house falloff modified its footing; all failure evidence retained. Other world regions retained.")
p=R/'blender/model_foreground_island_32b.py';assert not p.exists();p.write_text(s,encoding='utf-8')
