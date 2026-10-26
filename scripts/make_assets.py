import os, glob, numpy as np, scipy.io.wavfile as w
from build import *
os.makedirs('assets/previews',exist_ok=True); os.makedirs('assets/clips',exist_ok=True); os.makedirs('tmp',exist_ok=True)
rep=[]
for pre in sorted(glob.glob('out/*_pre.wav')):
    n=os.path.basename(pre)[:-8]
    if n.startswith('stem_'): continue
    I,P=master(pre,f'tmp/{n}.wav')
    if 'preview' in n: outs=enc(f'tmp/{n}.wav',f'assets/previews/{n}',['mp3'])
    else: outs=enc(f'tmp/{n}.wav',f'assets/clips/{n}',['ogg','m4a'])
    for o in outs:
        I2,P2=meas(o); rep.append((o,I2,P2)); print(o,I2,P2,flush=True)
