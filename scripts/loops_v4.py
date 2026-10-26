import os, sys, numpy as np, scipy.io.wavfile as w, subprocess
import arrange as A, loops as Lo
from build import meas, nsamp, SR
os.makedirs('assets/loops',exist_ok=True)
for name in (sys.argv[1:] or A.MIXES):
    cfg=dict(A.MIXES[name]); kind='mridang' if cfg.get('mr') else 'drums'
    y,Lp=Lo.build(kind,cfg); out,I,P,N=Lo.master_loop(y,'_tmp')
    base=f'assets/loops/{name}_loop'
    os.replace('/tmp/lmid.wav',f'tmp/{name}_loop.wav')
    for ext,a in (('ogg',['-c:a','libvorbis','-b:a','128k']),('m4a',['-c:a','aac','-b:a','160k','-movflags','+faststart'])):
        subprocess.run(['ffmpeg','-v','error','-y','-i',f'tmp/{name}_loop.wav']+a+[f'{base}.{ext}'],check=True)
        I2,P2=meas(f'{base}.{ext}'); n=nsamp(f'{base}.{ext}')
        print(f'{base}.{ext} {Lp:.3f}s N={N} dec={n} I={I2} TP={P2}',flush=True)
