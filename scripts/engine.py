import numpy as np, scipy.io.wavfile as w, scipy.signal as ss, sys, json
SR=44100
_c={}
def ld(n):
    if n not in _c:
        sr,x=w.read(f'wav/{n}.wav'); _c[n]=x.astype(np.float32)/32768
    return _c[n]
def db(g): return 10**(g/20)
def rms(s): return float(np.sqrt(np.mean(s**2))+1e-9)
def norm(s,t=-20): return s*db(t-20*np.log10(rms(s)))
def fade(s,fi=0.003,fo=0.05):
    s=s.copy(); n=len(s); a=min(int(fi*SR),n); b=min(int(fo*SR),n)
    if a: s[:a]*=np.linspace(0,1,a)[:,None]
    if b: s[n-b:]*=np.linspace(1,0,b)[:,None]**2
    return s
def sl(n,a,d,fi=0.003,fo=0.05): x=ld(n); return fade(x[int(a*SR):int((a+d)*SR)],fi,fo)
def expdecay(s,tau):  # clean tail (gate): exponential envelope
    t=np.arange(len(s))/SR; return s*np.exp(-t/tau)[:,None]
def rs(s,f):  # pitch/speed by factor f (>1 higher, shorter)
    if abs(f-1)<1e-4: return s
    n=int(len(s)/f); return ss.resample(s,n,axis=0).astype(np.float32)
def hp(s,fc,o=2): b,a=ss.butter(o,fc/(SR/2),'high'); return ss.lfilter(b,a,s,axis=0).astype(np.float32)
def lp(s,fc,o=2): b,a=ss.butter(o,fc/(SR/2),'low'); return ss.lfilter(b,a,s,axis=0).astype(np.float32)
def peq(s,f0,g,q=1.0):
    A=10**(g/40); w0=2*np.pi*f0/SR; al=np.sin(w0)/(2*q)
    b=[1+al*A,-2*np.cos(w0),1-al*A]; a=[1+al/A,-2*np.cos(w0),1-al/A]
    return ss.lfilter(b,a,s,axis=0).astype(np.float32)

# ---- stone mandir hall IR (algorithmic) ----
def make_ir(rt=2.1,seed=7):
    r=np.random.default_rng(seed); n=int(rt*1.3*SR); t=np.arange(n)/SR
    ir=np.zeros((n,2),np.float32)
    noise=r.standard_normal((n,2)).astype(np.float32)
    # frequency-dependent decay: split into bands, highs decay faster (stone: bright-ish but damped)
    bands=[(None,500,rt),(500,2500,rt*0.85),(2500,None,rt*0.55)]
    for lo,hi,T in bands:
        x=noise.copy()
        if lo: x=hp(x,lo,4)
        if hi: x=lp(x,hi,4)
        ir+=x*np.exp(-6.91*t/T)[:,None]
    pre=int(0.018*SR); ir=np.concatenate([np.zeros((pre,2),np.float32),ir])[:n]
    # early reflections (walls/pillars)
    for d,g in [(0.011,0.5),(0.019,0.42),(0.027,0.36),(0.034,0.3),(0.047,0.25),(0.061,0.2),(0.078,0.15)]:
        i=int(d*SR); ir[i,0]+=g*r.choice([-1,1]); ir[i+int(0.0013*SR*r.random()),1]+=g*r.choice([-1,1])
    ir[:int(0.004*SR)]*=np.linspace(0,1,int(0.004*SR))[:,None]
    return ir/np.sqrt(np.sum(ir**2)/2)
IR=make_ir()
def reverb(x):
    y=np.stack([ss.fftconvolve(x[:,c],IR[:,c])[:len(x)] for c in (0,1)],1).astype(np.float32)
    y=hp(y,180,2); y=lp(y,7000,2)   # keep wet out of the mud
    return y

class Mix:
    def __init__(s,T,seed=1):
        s.T=T; s.N=int((T+3)*SR); s.bus={}; s.r=np.random.default_rng(seed)
        s.duck={'bells':-3.5,'bed':-2.0}; s.dhol_drive=6.0; s._dg=None; s.busgain={'bells':2.0}
    def _b(s,n):
        if n not in s.bus: s.bus[n]=[np.zeros((s.N,2),np.float32),np.zeros((s.N,2),np.float32)]
        return s.bus[n]
    def put(s,x,t,g=0,pan=0.0,wet=0.2,ht=0.0,hv=0.0,hp_=0.0,bus='other'):
        r=s.r
        if ht: t+=r.normal(0,ht)
        if hv: g+=r.normal(0,hv)
        if hp_: x=rs(x,1+r.normal(0,hp_))
        t=max(0,t); i=int(t*SR); x=x[:max(0,s.N-i)]*db(g)
        a=(pan+1)*np.pi/4; L=np.cos(a)*np.sqrt(2); R=np.sin(a)*np.sqrt(2)
        y=np.empty_like(x); y[:,0]=x[:,0]*L; y[:,1]=x[:,1]*R
        d,sd=s._b(bus); d[i:i+len(y)]+=y; sd[i:i+len(y)]+=y*wet
    def _duckgain(s,depth):
        # v5 sidechain: envelope of the dry dhol bus (attack 2 ms, release 140 ms) ducks bells/jhalar/crash under each hit
        if s._dg is None:
            d=np.abs(s.bus['dhol'][0]).max(1); a=np.exp(-1/(0.002*SR)); r=np.exp(-1/(0.14*SR))
            e=ss.lfilter([1-r],[1,-r],d)            # release smoothing
            e=e/(np.percentile(e[e>1e-5],99) if (e>1e-5).any() else 1); s._dg=np.clip(e,0,1)
        return (db(depth)**s._dg)[:,None].astype(np.float32)
    def render(s,wetgain=0.0,fo=1.0,only=None,drive=0.0):
        out=np.zeros((s.N,2),np.float32)
        for n,(d,sd) in s.bus.items():
            if only and n not in only: continue
            y=d+reverb(sd)*db(wetgain)
            if n=='drums' and drive>0:   # drum-bus soft saturation: density + harmonics for small speakers
                k=db(drive); pk=np.abs(y).max()+1e-9; y=np.tanh(y/pk*k)/np.tanh(k)*pk
            if n=='dhol': y=dhol_bus(y,s.dhol_drive)
            if n in s.busgain: y=y*db(s.busgain[n])
            if n in s.duck and 'dhol' in s.bus and (not only or 'dhol' in only or True):
                y=y*s._duckgain(s.duck[n])
            out+=y
        out=out[:int(s.T*SR)]
        n=int(fo*SR)
        if n>0: out[-n:]*=np.linspace(1,0,n)[:,None]**1.5
        return out

def dhol_bus(y,drive=6.0):
    # v5 dhol lane: asymmetric tanh on the <250 Hz band -> 2nd/3rd harmonics (160-700 Hz) that phone speakers CAN play,
    # plus presence boost 1.5-3 kHz for stick/hand attack.
    lo=lp(y,250,2); hi=y-lo; k=db(drive); pk=np.abs(lo).max()+1e-9; u=lo/pk*k
    sat=(np.tanh(u+0.25)-np.tanh(0.25))/np.tanh(k)*pk
    sat=hp(sat,40,2)
    z=hi+sat*1.0+0.5*hp(sat,160,2)
    z=peq(z,2200,4.0,0.8); z=peq(z,450,2.5,1.0)
    return z
# ---- instrument library ----
def lib():
    L={}
    sh=ld('746592')
    L['shankh_full']=fade(sh[int(1.27*SR):int(8.62*SR)],0.03,0.4)
    ON=1.27
    def blow(d,f=1.0,end=False):
        if end and d>=1.4:   # attack + natural breath-out ending of the real blow
            xf=int(0.45*SR); B=sh[int(7.25*SR):int(8.62*SR)]
            A=sh[int(ON*SR):int(ON*SR)+int(d*SR)-len(B)+xf]
            r=np.linspace(0,1,xf)[:,None]
            a=np.concatenate([A[:-xf],A[-xf:]*(1-r)+B[:xf]*r,B[xf:]])
            return rs(fade(a,0.03,0.25),f)
        a=sh[int(ON*SR):int((ON+d)*SR)]; return rs(fade(a,0.03,min(0.35,d*0.3)),f)
    L['blow']=blow
    L['ghanta']=norm(fade(sl('466652',0.45,4.5,0.002,1.8)),-20)
    L['ghanta2']=norm(fade(sl('274316',1.75,2.0,0.002,0.9)),-21)   # leather mallet ghanta
    L['bellbed']=norm(sl('271627',0.0,8.9,0.3,1.0),-23)
    L['handbell']=norm(hp(sl('767307',0.0,11.3,0.2,1.0),300),-26)
    L['chime']=norm(sl('212541',1.5,4.0,0.002,1.5),-23)
    L['bells_far']=norm(lp(sl('390203',0.0,13.4,0.5,2.0),3500),-30)
    L['manj']=norm(sl('418152',0.0,0.9,0.001,0.45),-22)
    L['kart']=norm(sl('65492',0.32,0.28,0.001,0.08),-22)
    L['jhalar']=norm(hp(sl('696211',0.0,1.4,0.001,0.6),400),-22)
    L['jhalar_big']=norm(hp(sl('315630',0.0,4.0,0.001,2.0),250),-22)
    # nagada: low timpani C2 shortened + stick click + body thump (synth layer)
    tim=sl('369394',0.0,1.2,0.001,0.3); tim=expdecay(tim,0.35)
    t=np.arange(int(0.5*SR))/SR
    body=(np.sin(2*np.pi*(88*t+ 18*(1-np.exp(-t/0.03))*0.03))*np.exp(-t/0.18)).astype(np.float32)
    click=(np.random.default_rng(3).standard_normal(len(t))*np.exp(-t/0.004)).astype(np.float32)*0.3
    synth=np.stack([body+click,body+click],1)
    synth=np.pad(synth,((0,len(tim)-len(synth)),(0,0)))
    L['nag_dha']=norm(peq(hp(tim+0.5*norm(synth,20*np.log10(rms(tim))),75,3),115,2.5,0.9),-16)
    tt=sl('373936',0.0,0.6,0.001,0.15); tt=expdecay(tt,0.12)
    L['nag_ta']=norm(hp(rs(tt,1.12),150),-19)
    # dhol hits cleaned: short exp envelope (gate) + highpass
    L['dhol_dha']=norm(hp(expdecay(sl('418780',143.59,0.35,0.001,0.08),0.11),80),-18)
    L['dhol_tak']=norm(hp(expdecay(sl('418780',144.22,0.25,0.001,0.06),0.06),120),-20)
    # damru texture
    L['damru']=norm(hp(sl('746591',4.0,10.0,0.15,0.8),120),-19)
    # mridangam phrase (real performance)
    L['mridang']=norm(hp(sl('176272',0.0,12.0,0.01,0.5),50),-19)
    # tanpura: psuess Sa~120.4 Hz -> ~99.8 Hz (shankh/4)
    tp=ld('194435')[int(3*SR):int(33*SR)]; tp=rs(tp,99.8/120.4); tp=lp(hp(tp,70),4000)
    L['tanpura']=norm(fade(tp,1.5,1.5),-30)
    # room tone: soft brown-ish noise
    r=np.random.default_rng(11); n=int(25*SR); x=np.cumsum(r.standard_normal((n,2)),0); x=hp(x.astype(np.float32),40,2); x=lp(x,1200,2)
    L['room']=norm(x,-52)
    # ===== v3 drums: layered, punchy low-mid + 2-4 kHz attack, no HP above 60 Hz =====
    R=np.random.default_rng(31)
    def glide(f0,f1,tg,ta,dur):
        t=np.arange(int(dur*SR))/SR; f=f1+(f0-f1)*np.exp(-t/tg); ph=2*np.pi*np.cumsum(f)/SR
        return (np.sin(ph)*np.exp(-t/ta)).astype(np.float32)
    def burst(lo,hi,ta,dur):
        n=int(dur*SR); t=np.arange(n)/SR; x=R.standard_normal(n).astype(np.float32)
        b,a=ss.butter(2,[lo/(SR/2),hi/(SR/2)],'band'); return (ss.lfilter(b,a,x)*np.exp(-t/ta)).astype(np.float32)
    def st(m): m=np.asarray(m,np.float32); return np.stack([m,m],1)
    def fit(x,n): return np.pad(x,((0,max(0,n-len(x))),(0,0)))[:n]
    def lay(parts,dur):
        n=int(dur*SR); y=np.zeros((n,2),np.float32)
        for x,g in parts: y+=fit(norm(x,-20+g),n)
        a=int(0.0015*SR); y[:a]*=np.linspace(0,1,a)[:,None]
        return fade(y,0.0,0.06)
    tim=expdecay(sl('369394',0.0,0.9,0.001,0.2),0.30)
    deep=st(glide(95,58,0.04,0.20,0.8))
    dham=st(glide(210,150,0.025,0.085,0.5)+0.6*burst(120,420,0.05,0.5))
    stick=st(burst(2000,4500,0.006,0.08))
    L['nag3_D']=norm(peq(hp(lay([(tim,0),(deep,-3),(dham,-1),(stick,-6)],0.9),45,2),3000,2,1.0),-16)
    tF=expdecay(rs(sl('373936',0.0,0.5,0.001,0.12),1.12),0.12)
    dham2=st(glide(300,230,0.02,0.07,0.4)+0.5*burst(200,600,0.04,0.4))
    L['nag3_T']=norm(peq(lay([(tF,0),(dham2,-1),(stick,-6)],0.5),3200,3,1.0),-17)
    # dhol: real bass/treble hits + synth reinforcement
    dB_=expdecay(sl('418780',142.47,0.4,0.001,0.08),0.13); dB2=expdecay(sl('418780',144.79,0.4,0.001,0.08),0.13)
    bsyn=st(glide(130,82,0.03,0.13,0.45))
    slap=st(burst(1500,4500,0.010,0.08))
    L['dhol3_B']=[norm(peq(hp(lay([(x,0),(bsyn,-2),(slap,-5)],0.45),60,2),180,2,0.9),-17) for x in (dB_,dB2)]
    dK=expdecay(sl('418780',147.62,0.25,0.001,0.06),0.05); dK2=expdecay(sl('418780',144.24,0.25,0.001,0.06),0.05)
    crack=st(burst(1800,5500,0.012,0.12)); ring=st(glide(420,400,0.1,0.04,0.2))
    L['dhol3_K']=[norm(peq(hp(lay([(x,0),(crack,-3),(ring,-6)],0.25),60,2),3000,3,1.0),-19) for x in (dK,dK2)]
    # ===== v5 dhol: real bass+treble strokes (418780 dhol, 479246 dholak, 536872 dholak bass) + reinforcement =====
    def take(id,t0,d,tau): return expdecay(sl(id,t0,d,0.001,0.05),tau)
    bassR=[take('418780',142.47,0.4,0.14),take('418780',144.79,0.4,0.14),take('479246',1.039,0.34,0.16),
           take('479246',2.45,0.34,0.16),take('479246',3.86,0.34,0.16),take('536872',0.017,0.4,0.15)]
    trebR=[take('418780',147.62,0.25,0.06),take('418780',144.24,0.25,0.06),take('479246',0.551,0.2,0.07),
           take('479246',1.26,0.2,0.07),take('479246',2.664,0.2,0.07),take('479246',4.081,0.2,0.07)]
    bsyn5=st(glide(140,84,0.03,0.15,0.45)); slap5=st(burst(1400,3200,0.012,0.09)); body5=st(glide(330,260,0.02,0.06,0.3))
    L['dhol5_B']=[norm(peq(hp(lay([(x,0),(bsyn5,-3),(body5,-6),(slap5,-4)],0.45),55,2),2200,3,0.9),-15) for x in bassR]
    crack5=st(burst(1500,3500,0.010,0.10)); ring5=st(glide(440,420,0.1,0.05,0.2))
    L['dhol5_K']=[norm(peq(hp(lay([(x,0),(crack5,-2),(ring5,-7)],0.25),90,2),2400,3,1.0),-17) for x in trebR]
    # ===== v3 mridangam stroke library (re-sequenced from ajaysm/176272) =====
    import pickle
    st_=pickle.load(open('strokes272.pkl','rb')); x=ld('176272')
    lv=dict(THOM=-3.0,DIN=-6.0,TA=-7.0,KI=-8.0)
    for k in lv:
        a=[o for o in st_ if o['k']==k and o['L_s']>=0.12]; pks=np.array([o['pk'] for o in a])
        lo,hi=np.percentile(pks,[35,90]); a=[o for o in a if lo<=o['pk']<=hi][:10]
        segs=[]
        for o in a:
            n=int(min(o['L_s'],0.32)*SR); sg=x[int(o['t']*SR):int(o['t']*SR)+n]
            sg=fade(hp(sg,50),0.001,0.03); sg=sg/np.abs(sg).max()*db(lv[k]); segs.append(sg)
        L['m_'+k]=segs
    return L
