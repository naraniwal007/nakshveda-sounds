import numpy as np, scipy.io.wavfile as w, subprocess, re, sys, os
import arrange as A
from engine import *
L=A.L; X=3.0
def lbed(m,c,Lt):
    m.put(L['tanpura'][:int(Lt*SR)] if len(L['tanpura'])>=Lt*SR else np.tile(L['tanpura'],(2,1))[:int(Lt*SR)],0,c['tanpura'],wet=0.25,bus='bed')
    hb=np.tile(L['handbell'],(4,1))[:int(Lt*SR)]; m.put(hb,0,c['hand'],pan=0.4,wet=0.4,bus='bed')
    bb=np.tile(L['bellbed'],(5,1))[:int(Lt*SR)]; m.put(bb,0,c['ghanta']-6+c['bellbed'],pan=-0.2,wet=0.4,bus='bed')
    m.put(L['room'][:int(Lt*SR)],0,-4,wet=0.0,bus='bed')
    if c['damru']>-90:
        d=L['damru']; m.put(np.tile(d,(4,1))[:int(Lt*SR)],0,c['damru'],pan=-0.15,wet=0.2,bus='bed')
def build(kind,cfg):
    c=dict(A.BASE); c.update(cfg); b=60/c['tempo']
    if kind=='mridang':
        cyc=8*b; n=int(round(28/cyc)); Lp=n*cyc
    else:
        nb=int(round(30/b/16))*16; Lp=nb*b
    Lt=Lp+X+0.1; m=Mix(Lt,seed=c.get('seed',3)+100)
    if kind=='mridang':
        for i in range(n): A.mcycle(m,c,0.03+i*cyc,b,i)
    else: A.groove(m,c,0.03,nb)
    lbed(m,c,Lt)
    N=int(round(Lp*SR)); Xn=int(X*SR)
    ev=sum(m.render(c['wet'],0,only=[k],drive=c['drive']) for k in m.bus if k!='bed')
    bd=m.render(c['wet'],0,only=['bed'])
    y=ev[:N].copy(); y[:Xn]+=ev[N:N+Xn]                   # wrap event/reverb tails
    f=np.linspace(0,np.pi/2,Xn)[:,None]; z=bd[:N].copy()
    z[:Xn]=bd[:Xn]*np.sin(f)+bd[N:N+Xn]*np.cos(f)          # equal-power crossfade for continuous beds
    return y+z, Lp
def master_loop(y,name):
    y=y/(np.abs(y).max()*1.12); t3=np.tile(y,(3,1)); N=len(y)
    w.write('/tmp/l3.wav',SR,t3.astype(np.float32)); g=7.0
    for it in range(6):
        af=(f"highpass=f=55:poles=2,acompressor=threshold=-20dB:ratio=1.8:attack=20:release=220:knee=6:makeup=1,"
            f"aresample=176400,volume={g:.2f}dB,alimiter=limit=0.77:attack=4:release=90:level=false,aresample=44100")
        subprocess.run(['ffmpeg','-v','error','-y','-i','/tmp/l3.wav','-af',af,'-c:a','pcm_f32le','/tmp/l3m.wav'],check=True)
        sr,mm=w.read('/tmp/l3m.wav'); mid=mm[N:2*N]
        w.write('/tmp/lmid.wav',SR,mid.astype(np.float32))
        r=subprocess.run(['ffmpeg','-hide_banner','-i','/tmp/lmid.wav','-af','ebur128=peak=true:framelog=quiet','-f','null','-'],capture_output=True,text=True).stderr
        s=r[r.rfind('Summary'):]; I=float(re.search(r'I:\s+(-?[\d.]+)',s).group(1)); P=float(re.search(r'Peak:\s+(-?[\d.]+)',s).group(1))
        if abs(I+14)<0.15: break
        g+=-14-I
    out=f'loops/{name}_loop.ogg'; os.makedirs('loops',exist_ok=True)
    subprocess.run(['ffmpeg','-v','error','-y','-i','/tmp/lmid.wav','-c:a','libvorbis','-b:a','128k',out],check=True)
    return out,I,P,N
LOOPS={
 'aarti_mode_v3':('drums',{}),
 'shiv_aarti_v3':('drums',dict(tempo=112,damru=0,kart=-99,dhol=-3,seed=4)),
 'ganesh_aarti_v3':('drums',dict(tempo=108,manj=2,kart=1,seed=6)),
 'durga_aarti_v3':('drums',dict(tempo=120,nag=1.5,jhal=1,jhal_off=-4,seed=7)),
 'hanuman_aarti_v3':('drums',dict(tempo=116,dhol=1,kart=0,ghanta=-1,seed=8)),
 'lakshmi_aarti_v3':('drums',dict(tempo=96,ghanta=-5,hand=0,chime=-3,nag=-4,dhol=-5,jhal=-5,kart=-6,tanpura=0,manj=-2,seed=9)),
 'jagdish_aarti_v3':('drums',dict(tempo=104,ghanta=2,seed=10)),
 'mridang_aarti_v3':('mridang',dict(tempo=147.2,mridang=0,tanpura=-4,hand=-8,drive=2.0,dwet=0.06,seed=21)),
}
if __name__=='__main__':
    os.makedirs('loops',exist_ok=True)
    for name in (sys.argv[1:] or LOOPS):
        k,cfg=LOOPS[name]; y,Lp=build(k,cfg); out,I,P,N=master_loop(y,name)
        print(f'{out}: {Lp:.3f}s ({N} samples) I={I} TP={P}')
