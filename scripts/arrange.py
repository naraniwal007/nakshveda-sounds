import numpy as np, scipy.io.wavfile as w, sys
from engine import *
L=lib()
# v3: drums drive the rhythm. levels in dB relative to library norm
BASE=dict(tempo=112,nag=2,dhol=5,ghost=-11,jhal=-1,jhal_off=-99,ghanta=0,hand=-6,chime=-99,manj=-1,kart=-3,damru=-99,
          tanpura=-3,bellbed=-3,shankh=0,bigsam=0,wet=0,dwet=0.05,bwet=0.45,drive=4.0)
NAG=[('D',2),('D',-1),('T',-1),(None,0),('D',0),('D',-1),('T',-1),('T',-4)]      # dha dha dhin . dha dha dhin dhin
KEH=[('BK',2),('B',-1),('K',0),('k',-4),('K',-1),('k',-4),('BK',1),('K',-1)]     # keherwa: dha ge na ti | na ka dhi na (v5: denser, louder treble)
def dr(m,c,s,t,g,pan=0.0,ht=0.007,hv=1.2):
    if s=='D': m.put(L['nag3_D'],t,c['nag']+g,pan=pan,wet=c['dwet'],ht=ht,hv=hv,hp_=0.008,bus='drums')
    elif s=='T': m.put(L['nag3_T'],t,c['nag']+g,pan=pan,wet=c['dwet'],ht=ht,hv=hv,hp_=0.008,bus='drums')
    else:
        nb=len(L['dhol5_B']); nk=len(L['dhol5_K'])
        if 'B' in s: m.put(L['dhol5_B'][m.r.integers(nb)],t,c['dhol']+g,pan=-0.05,wet=c['dwet']*0.6,ht=ht*0.7,hv=hv*0.6,hp_=0.005,bus='dhol')
        if 'K' in s or 'k' in s:
            m.put(L['dhol5_K'][m.r.integers(nk)],t+0.003,c['dhol']+g+(-4 if s=='k' else 0),pan=0.08,wet=c['dwet']*0.6,ht=ht*0.7,hv=hv*0.6,hp_=0.006,bus='dhol')
def bells(m,c,bt,k,e):
    side=1 if k%2==0 else -1
    g=L['ghanta'] if k%3!=2 else L['ghanta2']
    m.put(g,bt+0.012,c['ghanta']-7+(0 if side>0 else -1.5),pan=0.3*side,wet=c['bwet'],ht=0.022,hv=1.8,hp_=0.006,bus='bells')
    m.put(L['manj'],bt,c['manj']-2+(0 if k%2==0 else -3),pan=-0.25,wet=0.25,ht=0.008,hv=1.5,hp_=0.01,bus='bells')
    m.put(L['kart'],bt+e,c['kart']-3,pan=0.35,wet=0.2,ht=0.008,hv=2,hp_=0.01,bus='bells')
    m.put(L['jhalar'],bt,c['jhal']-2,pan=0.15,wet=0.3,ht=0.007,hv=1.5,hp_=0.01,bus='bells')
    if c['jhal_off']>-90: m.put(L['jhalar'],bt+e,c['jhal']+c['jhal_off'],pan=0.1,wet=0.3,ht=0.007,hv=1.5,hp_=0.01,bus='bells')
def groove(m,c,t0,nbeats):
    b=60/c['tempo']; e=b/2
    for k in range(nbeats):
        bt=t0+k*b; bells(m,c,bt,k,e)
        fill=c.get('fills',True) and (k//4)%4==3 and k%4>=2
        if fill:   # nagada/dhol fill in last 2 beats of every 4th bar: 16ths
            for q in range(4):
                tq=bt+q*e/2; dr(m,c,'D' if q%2==0 else 'T',tq,-2+q*0.7+(k%4-2)); dr(m,c,'K' if q%2 else 'BK',tq,-4+q*0.5)
            continue
        for j in (0,1):
            i=(k*2+j)%8; acc=2 if i==0 else 0
            s,g=NAG[i]
            if s: dr(m,c,s,bt+j*e,g+(1 if i==0 else 0))
            s,g=KEH[i]; dr(m,c,s,bt+j*e,g+acc*0.5)
            if c['ghost']>-90 and i not in (7,): dr(m,c,'k',bt+j*e+e/2,c['ghost']+4)   # v5: 16th ghost treble keeps the groove steady
def pickup(m,c,f0):
    # half-bar nagada/dhol roll into sam of the groove (crescendo)
    b=60/c['tempo']; e=b/2
    for j,(s,g) in enumerate([('T',-9),('T',-7),('D',-5),('D',-3)]):
        t=f0-(4-j)*e; dr(m,c,s,t,g); dr(m,c,'BK',t,g-1)
def tihai(m,c,sam):
    b=60/c['tempo']; e=b/2; st=sam-10*e
    for r in range(3):
        for j,(s,gv) in enumerate([('D',0),('T',-1),('D',1)]):
            t=st+(r*4+j)*e
            if r==2 and j==2: continue
            dr(m,c,s,t,gv+r,ht=0.004,hv=0.8); dr(m,c,'BK',t,gv+r-1,ht=0.004,hv=0.8)
            m.put(L['jhalar'],t,c['jhal']-3+r,pan=0.15,wet=0.3,ht=0.005,hv=1,bus='bells')
            m.put(L['manj'],t,c['manj']-3,pan=-0.25,wet=0.25,ht=0.005,hv=1,bus='bells')
        m.put(L['ghanta'],st+r*4*e,c['ghanta']-6,pan=0.2*(r-1),wet=c['bwet'],ht=0.01,hp_=0.005,bus='bells')
    # SAM
    dr(m,c,'D',sam,3,ht=0,hv=0); dr(m,c,'D',sam+0.006,-2,ht=0,hv=0); dr(m,c,'BK',sam,2,ht=0,hv=0)
    m.put(L['jhalar_big'],sam,c['jhal']+c['bigsam']-1,pan=0.1,wet=0.45,bus='bells')
    m.put(L['ghanta'],sam+0.01,c['ghanta']-2,pan=-0.15,wet=0.5,bus='bells')
    m.put(L['ghanta'],sam+0.03,c['ghanta']-6,pan=0.25,wet=0.5,hp_=0.02,bus='bells')
    m.put(L['manj'],sam,c['manj']+1,pan=-0.25,wet=0.3,bus='bells')
    if c['chime']>-90: m.put(L['chime'],sam+0.02,c['chime'],pan=0.3,wet=0.45,bus='bells')
def shankh(m,c,t,blows):
    for i,(d,f) in enumerate(blows):
        last=i==len(blows)-1
        m.put(L['blow'](d,f,end=last),t,c['shankh']-1-(0 if last else 1),wet=0.45,hv=0.5,bus='shankh'); t+=d+0.22
    return t
def bed(m,c,a,b):
    m.put(L['tanpura'][:int((b-a+2)*SR)],a,c['tanpura'],wet=0.25,bus='bed')
    hb=L['handbell']; seg=fade(np.tile(hb,(3,1))[:int((b-a)*SR)],0.6,1.2); m.put(seg,a,c['hand'],pan=0.4,wet=0.4,bus='bells')
    m.put(L['bellbed'][:int(min(8.9,b-a)*SR)],a,c['ghanta']-6+c['bellbed'],pan=-0.2,wet=0.4,bus='bells')
def ambience(m,a,b,g=0):
    m.put(fade(L['room'][:int((b-a)*SR)],0.8,0.8),a,g,wet=0.0,bus='amb')
    m.put(fade(L['bells_far'][:int(min(13.0,b-a)*SR)],0.5,1.0),a,g-1,pan=-0.3,wet=0.6,bus='amb')
def drums_section(m,c,f0,sam):
    b=60/c['tempo']; e=b/2; ts=sam-10*e
    n=int(round((ts-f0)/b)); f0=ts-n*b
    pickup(m,c,f0); groove(m,c,f0,n); tihai(m,c,sam)
    # dhol keeps keherwa under the tihai lightly
    for k in range(5):
        for j in (0,1):
            s,g=KEH[(k*2+j)%8]
            if 'B' not in s: dr(m,c,s,ts+k*b+j*e,g-4)
    return f0,n
BLOWS3=[(1.5,1.0),(1.5,0.995),(2.6,1.0)]
def damru_on(m,c,a,b_):
    if c['damru']>-90:
        d=np.tile(L['damru'],(3,1)); m.put(fade(d[:int((b_-a)*SR)],0.3,0.5),a,c['damru'],pan=-0.15,wet=0.2,bus='bed')
def piece(kind,cfg={},only=None):
    c=dict(BASE); c.update(cfg); b=60/c['tempo']; e=b/2
    if kind=='full20':          # v4: starts directly with the shankh (no pre-ambience)
        T=20.0; m=Mix(T,seed=c.get('seed',5))
        te=shankh(m,c,0.02,BLOWS3); bed(m,c,te-2.4,T)
        sam=17.0; f0,_=drums_section(m,c,te-0.55,sam); damru_on(m,c,f0-0.5,sam+1.0); fo=1.6
    elif kind=='full10':        # v5: 10 s - 3 short shankh blows, then dhol-led groove, tihai, sam
        T=10.0; m=Mix(T,seed=c.get('seed',5)+1)
        te=shankh(m,c,0.02,[(0.95,1.0),(0.95,0.995),(1.6,1.0)]); bed(m,c,te-1.2,T)
        sam=8.75; f0,_=drums_section(m,c,te-0.4,sam); damru_on(m,c,f0-0.3,sam+0.8); fo=1.0
    elif kind=='mridang20': return mridang20(c)
    elif kind=='intro':         # 3 shankh blows only
        T=6.9; m=Mix(T,seed=1); shankh(m,c,0.02,BLOWS3); fo=0.5
    elif kind=='naad':          # single long blow with natural ending
        T=5.6; m=Mix(T,seed=2); shankh(m,c,0.02,[(4.6,1.0)]); fo=0.4
    elif kind=='ending':        # tihai -> sam -> bell tail
        T=10*e+0.06+3.6; m=Mix(T,seed=c.get('seed',3)+50); sam=10*e+0.06
        bed(m,c,0,T)
        if c.get('mr'): mtihai(m,c,sam,b)
        else:
            tihai(m,c,sam)
            for k in range(5):
                for j in (0,1):
                    s_,g=KEH[(k*2+j)%8]
                    if 'B' not in s_: dr(m,c,s_,0.06+k*b+j*e,g-4)
        damru_on(m,c,0,sam+0.6); fo=2.2
    return m.render(wetgain=c['wet'],fo=fo,only=only,drive=c['drive'])
# ---------- mridangam (re-sequenced adi talam, tishra nadai: 8 beats x 3) ----------
MB=[['THOM+DIN','.','KI'],['TA','KI','TA'],['DIN','.','TA'],['THOM','KI','TA'],
    ['THOM+DIN','.','KI'],['TA','ki','TA'],['DIN','.','TA'],['THOM','KI','TA']]
MVAR=[{6:['TA','KI','TA'],7:['DIN','KI','TA']},{2:['DIN','ki','TA'],6:['THOM','.','TA']},
      {6:['THOM','TA','KI'],7:['THOM','TA','KI']},{1:['TA','.','TA'],5:['KI','TA','KI']}]
def mstroke(m,c,tok,t,g=0):
    for part in tok.split('+'):
        soft=part.islower(); k=part.upper(); lib=L['m_'+k]
        m.put(lib[m.r.integers(len(lib))],t,c['mridang']+g+(-7 if soft else 0),pan=0.05,wet=c['dwet']+0.08,ht=0.006,hv=1.3,hp_=0.004,bus='drums')
def mcycle(m,c,t0,p,v):
    bar=[list(b) for b in MB]
    for kk,vv in MVAR[v%len(MVAR)].items(): bar[kk]=list(vv)
    for bi,bt in enumerate(bar):
        for j,tok in enumerate(bt):
            if tok=='.':
                if m.r.random()<0.3: tok='ki'
                else: continue
            mstroke(m,c,tok,t0+(bi*3+j)*p/3,(1.5 if (bi in (0,4) and j==0) else 0))
        tb=t0+bi*p   # bells on the tala: manjira every beat, ghanta on laghu/drutam starts
        m.put(L['manj'],tb,c['manj']-3+(0 if bi%2==0 else -4),pan=-0.25,wet=0.25,ht=0.006,hv=1.2,hp_=0.01,bus='bells')
        if bi in (0,4,6): m.put(L['ghanta'],tb+0.01,c['ghanta']-9,pan=0.3*(-1)**bi,wet=c['bwet'],ht=0.02,hv=1.5,hp_=0.006,bus='bells')
        if bi==0: m.put(L['jhalar'],tb,c['jhal']-6,pan=0.15,wet=0.3,ht=0.006,bus='bells')
def mtihai(m,c,sam,p):
    s3=p/3; ph=['TA','KI','TA','THOM']; st=sam-(3*len(ph)+2)*s3
    for r in range(3):
        for j,tok in enumerate(ph): mstroke(m,c,tok,st+(r*(len(ph)+1)+j)*s3,r*0.8)
    mstroke(m,c,'THOM+DIN',sam,3)
    m.put(L['ghanta'],sam,c['ghanta']-2,wet=0.5,bus='bells'); m.put(L['manj'],sam,c['manj']+1,pan=-0.25,wet=0.3,bus='bells')
    m.put(L['chime'],sam+0.02,-4,pan=0.3,wet=0.45,bus='bells'); m.put(L['jhalar_big'],sam,-6,wet=0.45,bus='bells')
def mridang20(c):
    T=20.0; m=Mix(T,seed=21); p=60/c['tempo']*1.0
    te=shankh(m,c,0.02,BLOWS3); bed(m,c,te-2.4,T)
    sam=17.0; cyc=8*p; tstart=sam-(3*4+2)*p/3
    n=int((tstart-(te-0.5))//cyc)+1; t0=tstart-n*cyc
    for i in range(n): mcycle(m,c,t0+i*cyc,p,i)
    # trim cycle overlapping the tihai: last cycle runs to tstart; mtihai overlays
    mtihai(m,c,sam,p); return m.render(wetgain=c['wet'],fo=1.6,drive=c['drive'])
MIXES={
 'mandir':dict(seed=5),
 'shiv':dict(tempo=112,damru=-2,kart=-99,dhol=5,seed=4),
 'ganesh':dict(tempo=108,manj=2,kart=1,seed=6),
 'durga':dict(tempo=120,nag=1.5,jhal=1,jhal_off=-4,bigsam=2,seed=7),
 'hanuman':dict(tempo=116,dhol=6,kart=0,ghanta=-1,seed=8),
 'lakshmi':dict(tempo=96,ghanta=-5,hand=0,chime=-3,nag=-4,dhol=2,jhal=-5,kart=-6,tanpura=0,manj=-2,seed=9),
 'jagdish':dict(tempo=104,ghanta=2,shankh=1,seed=10),
 'mridang':dict(tempo=147.2,mridang=3,shankh=-2,tanpura=-4,hand=-8,drive=2.0,dwet=0.06,seed=21,mr=1),
}
JOBS={f'{n}_preview_20s':('mridang20' if n=='mridang' else 'full20',c) for n,c in MIXES.items()}
JOBS.update({f'{n}_ending':('ending',c) for n,c in MIXES.items()})
JOBS['mandir_preview_10s']=('full10',MIXES['mandir']); JOBS['shankh_intro']=('intro',{}); JOBS['shankh_naad']=('naad',{})
if __name__=='__main__':
    import os; os.makedirs('out',exist_ok=True)
    for name in (sys.argv[1:] or JOBS):
        k,cfg=JOBS[name]; y=piece(k,cfg); sc=np.abs(y).max()*1.12; y=y/sc
        w.write(f'out/{name}_pre.wav',SR,y.astype(np.float32))
        for st in ([] if k!='full20' else ('drums','bells')):
            z=piece(k,cfg,only=[st])/sc; w.write(f'out/stem_{name}_{st}.wav',SR,z.astype(np.float32))
        print(name,len(y)/SR)
