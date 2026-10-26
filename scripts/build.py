# v4 final asset build: master -> encode -> verify -> manifest
import numpy as np, scipy.io.wavfile as w, subprocess, re, os, sys, glob, json, hashlib
SR=44100
CH="highpass=f=55:poles=2,acompressor=threshold=-20dB:ratio=1.8:attack=20:release=220:knee=6:makeup=1,aresample=176400,volume={g:.2f}dB,alimiter=limit={lim}:attack=4:release=90:level=false,aresample=44100"
def meas(f):
    r=subprocess.run(['ffmpeg','-hide_banner','-i',f,'-af','ebur128=peak=true:framelog=quiet','-f','null','-'],capture_output=True,text=True).stderr
    s=r[r.rfind('Summary'):]; return float(re.search(r'I:\s+(-?[\d.]+)',s).group(1)),float(re.search(r'Peak:\s+(-?[\d.]+)',s).group(1))
def master(src_wav,dst_wav,lim=0.79,target=-14.0,mid=None):
    g=7.0
    for _ in range(7):
        subprocess.run(['ffmpeg','-v','error','-y','-i',src_wav,'-af',CH.format(g=g,lim=lim),'-c:a','pcm_f32le',dst_wav],check=True)
        if mid:   # loops: keep middle copy of 3x tile
            sr,x=w.read(dst_wav); N=mid; w.write(dst_wav,SR,x[N:2*N].astype(np.float32))
        I,P=meas(dst_wav)
        if abs(I-target)<0.15: break
        g+=target-I
    return I,P
def enc(wav,base,kinds):
    outs=[]
    for k in kinds:
        o=f'{base}.{k}'
        a={'mp3':['-c:a','libmp3lame','-b:a','192k'],'ogg':['-c:a','libvorbis','-b:a','128k'],'m4a':['-c:a','aac','-b:a','160k','-movflags','+faststart']}[k]
        subprocess.run(['ffmpeg','-v','error','-y','-i',wav]+a+[o],check=True); outs.append(o)
    return outs
def nsamp(f):
    x=subprocess.run(['ffmpeg','-v','error','-i',f,'-f','f32le','-ac','2','-ar','44100','-'],capture_output=True).stdout
    return len(x)//8
