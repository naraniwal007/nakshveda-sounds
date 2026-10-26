# AAC frames are 1024 samples; ffmpeg's native aac leaves end padding untrimmed.
# Periodic (FFT) resample each loop to a multiple of 1024 samples (<0.04% tempo change) so the m4a decodes sample-exact.
import glob, numpy as np, scipy.io.wavfile as w, scipy.signal as ss, subprocess, os
from build import meas, nsamp, SR
for f in sorted(glob.glob('tmp/*_loop.wav')):
    name=os.path.basename(f)[:-4]; sr,x=w.read(f); N=len(x); M=int(round(N/1024))*1024
    y=ss.resample(x.astype(np.float64),M,axis=0).astype(np.float32)
    w.write(f'tmp/{name}_aac.wav',SR,y); o=f'assets/loops/{name}.m4a'
    subprocess.run(['ffmpeg','-v','error','-y','-i',f'tmp/{name}_aac.wav','-c:a','aac','-b:a','160k','-movflags','+faststart',o],check=True)
    d=subprocess.run(['ffmpeg','-v','error','-i',o,'-f','f32le','-ac','2','-'],capture_output=True).stdout
    z=np.frombuffer(d,np.float32).reshape(-1,2)
    c=np.correlate(z[:20000,0],y[:20000,0][::1],'full'); lag=int(np.argmax(np.correlate(z[2048:12000,0],y[:14096,0],'valid')))
    I,P=meas(o); print(o,N,'->',M,'dec',len(z),'TP',P,'I',I,flush=True)
