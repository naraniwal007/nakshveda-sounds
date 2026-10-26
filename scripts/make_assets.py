import os, glob
from build import *
os.makedirs('assets/previews',exist_ok=True); os.makedirs('assets/clips',exist_ok=True); os.makedirs('tmp',exist_ok=True)
for pre in sorted(glob.glob('out/*_pre.wav')):
    n=os.path.basename(pre)[:-8]
    if n.startswith('stem_'): continue
    lim=0.79
    for _ in range(5):
        master(pre,f'tmp/{n}.wav',lim=lim)
        kinds=['mp3'] if 'preview' in n else ['ogg','m4a']
        outs=enc(f'tmp/{n}.wav',f'assets/{"previews" if "preview" in n else "clips"}/{n}',kinds)
        ms=[meas(o) for o in outs]
        if max(p for _,p in ms)<=-1.1: break
        lim-=0.04
    for o,(I,P) in zip(outs,ms): print(o,I,P,'lim',round(lim,2),flush=True)
