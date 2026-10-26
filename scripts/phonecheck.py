# phone-speaker check: 200 Hz HP (4th order) + 8 kHz LP sim; per-stem energy in the groove window, relative to the full mix
import sys, os, numpy as np, scipy.signal as ss, json
ver=sys.argv[1]; os.chdir(f'/workspace/samples/aarti_preview/{ver}'); sys.path.insert(0,'.')
import arrange as A
SR=44100; W=(7.0,16.5)
def phone(x):
    b,a=ss.butter(4,200/(SR/2),'high'); x=ss.lfilter(b,a,x,axis=0); b,a=ss.butter(2,8000/(SR/2),'low'); return ss.lfilter(b,a,x,axis=0)
def band(x,lo,hi): b,a=ss.butter(2,[lo/(SR/2),hi/(SR/2)],'band'); return ss.lfilter(b,a,x,axis=0)
def rdb(x): x=x[int(W[0]*SR):int(W[1]*SR)]; return float(20*np.log10(np.sqrt(np.mean(x**2))+1e-12))
def p95(x):
    x=x[int(W[0]*SR):int(W[1]*SR)].mean(1); f=x[:len(x)//441*441].reshape(-1,441); return float(20*np.log10(np.percentile(np.sqrt((f**2).mean(1)),95)+1e-12))
name=sys.argv[2] if len(sys.argv)>2 else 'mandir'
cfg=dict(A.MIXES.get(name,A.MIXES['mandir'])); kind=sys.argv[3] if len(sys.argv)>3 else 'full20'
if kind=='full10': W=(4.5,8.6)
full=A.piece(kind,cfg)
if ver=='v5':
    st={'dhol':A.piece(kind,cfg,only=['dhol']),'nagada':A.piece(kind,cfg,only=['drums'])}
else:
    st={'dhol':A.piece(kind,dict(cfg,nag=-200),only=['drums']),'nagada':A.piece(kind,dict(cfg,dhol=-200),only=['drums'])}
st['bells']=A.piece(kind,cfg,only=['bells']); st['bed']=A.piece(kind,cfg,only=['bed']); st['shankh']=A.piece(kind,cfg,only=['shankh'])
F=phone(full); ref=rdb(F); out={}
for k,v in st.items():
    P=phone(v); out[k]=dict(phone_rel_mix=round(rdb(P)-ref,1),full_rel_mix=round(rdb(v)-rdb(full),1),
        attack_1k5_3k_rel_mix=round(rdb(band(v,1500,3000))-rdb(band(full,1500,3000)),1),punch_p95_phone=round(p95(P)-p95(F),1))
out['_phone_loss_mix_dB']=round(ref-rdb(full),1)
out['_dhol_minus_bells_phone']=round(out['dhol']['phone_rel_mix']-out['bells']['phone_rel_mix'],1)
print(json.dumps({ver+':'+name:out}))
