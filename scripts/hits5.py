import numpy as np, scipy.io.wavfile as w, scipy.signal as ss, sys
SR=44100
def band(x,lo,hi):
    b,a=ss.butter(2,[lo/(SR/2),hi/(SR/2)],'band'); return ss.lfilter(b,a,x)
def onsets(id,maxn=40):
    sr,x=w.read(f'wav/{id}.wav'); x=x.astype(np.float32).mean(1)/32768
    h=256; S=np.abs(ss.stft(x,SR,nperseg=1024,noverlap=1024-h)[2]); fl=np.maximum(0,np.diff(np.log(S+1e-6),axis=1)).sum(0)
    fl=(fl-np.median(fl)); pk,_=ss.find_peaks(fl,height=np.percentile(fl,97),distance=int(0.09*SR/h))
    t=pk*h/SR; res=[]
    lo=band(x,60,200); pr=band(x,1500,3000)
    for i,ti in enumerate(t):
        a=int(ti*SR); nxt=t[i+1] if i+1<len(t) else ti+1
        gap=nxt-ti; win=slice(a,a+int(min(gap,0.25)*SR))
        pre=slice(max(0,a-int(0.05*SR)),a-int(0.005*SR))
        el=20*np.log10(np.sqrt(np.mean(lo[win]**2))+1e-9); ep=20*np.log10(np.sqrt(np.mean(pr[win]**2))+1e-9)
        epre=20*np.log10(np.sqrt(np.mean(x[pre]**2))+1e-9); ewin=20*np.log10(np.sqrt(np.mean(x[win]**2))+1e-9)
        res.append((round(ti,3),round(gap,3),round(el,1),round(ep,1),round(ewin-epre,1)))
    return res
for id in sys.argv[1:]:
    r=onsets(id); print('==',id,len(r))
    for q in r[:80]: print(q)
