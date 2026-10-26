import numpy as np, subprocess, sys, re
def dec(f):
    r=subprocess.run(['ffmpeg','-v','error','-i',f,'-f','f32le','-ac','1','-ar','44100','-'],capture_output=True).stdout
    return np.frombuffer(r,np.float32)
def bands(f,a,b):
    x=dec(f)[int(a*44100):int(b*44100)]; S=np.abs(np.fft.rfft(x))**2; fr=np.fft.rfftfreq(len(x),1/44100); T=S.sum()
    d=lambda lo,hi:10*np.log10(S[(fr>=lo)&(fr<hi)].sum()/T)
    ab=lambda lo,hi:10*np.log10(S[(fr>=lo)&(fr<hi)].sum()/len(x)**2*2)
    return round(d(60,250),1),round(ab(60,250),1),round(d(2000,4000),1)
def lufs(f):
    r=subprocess.run(['ffmpeg','-hide_banner','-i',f,'-af','ebur128','-f','null','-'],capture_output=True,text=True).stderr
    return float(re.search(r'I:\s+(-?[\d.]+)',r[r.rfind('Summary'):]).group(1))
for f,a,b in [(x.split(':')[0],float(x.split(':')[1]),float(x.split(':')[2])) for x in sys.argv[1:]]:
    print(f, 'share60-250 dB, abs60-250 dBFS, share2-4k dB =',bands(f,a,b))
