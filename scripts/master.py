import subprocess, re, sys, glob, os
def run(pre,out,g):
    af=(f"highpass=f=55:poles=2,acompressor=threshold=-20dB:ratio=1.8:attack=20:release=220:knee=6:makeup=1,"
        f"aresample=176400,volume={g:.2f}dB,alimiter=limit=0.81:attack=4:release=90:level=false,aresample=44100")
    subprocess.run(['ffmpeg','-v','error','-y','-i',pre,'-af',af,'-ar','44100','-ac','2','-c:a','libmp3lame','-b:a','192k',out],check=True)
    r=subprocess.run(['ffmpeg','-hide_banner','-i',out,'-af','ebur128=peak=true:framelog=quiet','-f','null','-'],capture_output=True,text=True).stderr
    s=r[r.rfind('Summary'):]
    I=float(re.search(r'I:\s+(-?[\d.]+)',s).group(1)); P=float(re.search(r'Peak:\s+(-?[\d.]+)',s).group(1)); LRA=float(re.search(r'LRA:\s+(-?[\d.]+)',s).group(1))
    return I,P,LRA
for pre in sorted(glob.glob('out/*_pre.wav')):
    name=os.path.basename(pre)[:-8]; out=f'{name}.mp3'; g=8.0
    for it in range(6):
        I,P,LRA=run(pre,out,g)
        if abs(I+14)<0.15: break
        g+= (-14-I)
    # measure limiter gain reduction approx: compare with no limiter
    print(f'{out}: I={I} LUFS TP={P} dBTP LRA={LRA} gain={g:.2f}')
