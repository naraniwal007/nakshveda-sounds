import glob, numpy as np, scipy.io.wavfile as w, subprocess, os
from build import meas, SR
for f in sorted(glob.glob('tmp/*_loop_aac.wav')):
    name=os.path.basename(f)[:-8]; sr,y=w.read(f); M=len(y)
    w.write('/tmp/a3.wav',SR,np.tile(y,(3,1)))
    subprocess.run(['ffmpeg','-v','error','-y','-i','/tmp/a3.wav','-af','aresample=176400,alimiter=limit=0.80:attack=2:release=60:level=false,aresample=44100','-c:a','pcm_f32le','/tmp/a3m.wav'],check=True)
    sr,t=w.read('/tmp/a3m.wav'); y2=t[M:2*M].astype(np.float32); w.write(f,SR,y2)
    o=f'assets/loops/{name}.m4a'
    subprocess.run(['ffmpeg','-v','error','-y','-i',f,'-c:a','aac','-b:a','160k','-movflags','+faststart',o],check=True)
    z=np.frombuffer(subprocess.run(['ffmpeg','-v','error','-i',o,'-f','f32le','-ac','2','-'],capture_output=True).stdout,np.float32).reshape(-1,2)
    seg=y2[44100:88200,0]; r=[np.dot(z[44100+k:88200+k,0],seg) for k in range(-1100,1101)]; lag=int(np.argmax(r))-1100
    jump=np.abs(z[0]-z[-1]).max(); p99=np.percentile(np.abs(np.diff(z[:,0])),99)
    I,P=meas(o); print(name,'M',M,'dec',len(z),'lag',lag,'seam',round(float(jump),4),'p99',round(float(p99),4),'I',I,'TP',P,flush=True)
