import json, hashlib, os, glob, subprocess, sys
root=sys.argv[1] if len(sys.argv)>1 else '.'
def dur(f): return float(subprocess.run(['ffprobe','-v','error','-show_entries','format=duration','-of','csv=p=0',f],capture_output=True,text=True).stdout)
def samples(f): return len(subprocess.run(['ffmpeg','-v','error','-i',f,'-f','s16le','-ac','1','-ar','44100','-'],capture_output=True).stdout)//2
items=[]
for f in sorted(glob.glob(f'{root}/assets/*/*')):
    rel=os.path.relpath(f,root); b=open(f,'rb').read(); n=os.path.basename(f)
    cat=rel.split('/')[1]; stem,ext=os.path.splitext(n)
    s=samples(f)
    items.append(dict(name=stem,file=rel,format=ext[1:],category=cat,bytes=len(b),sha256=hashlib.sha256(b).hexdigest(),
        duration=round(s/44100,4),samples=s,sample_rate=44100,channels=2,loop=(cat=='loops'),loudness_lufs=-14.0))
m=dict(pack='nakshveda-aarti-sounds',version='packs-v1',generated='2026-10-26',license='Mixes © AXIORA GLOBAL SYSTEMS PVT LTD; all source recordings CC0 1.0 (see SOURCES.md)',
       notes='v5: dhol-dominant mixes (own dhol bus with 1.5-3 kHz attack, low-end saturation, bells/bed side-chain ducked under dhol hits, steady keherwa with ghost strokes); new mandir_preview_10s. Every preview starts directly with 3 shankh blows. Loops are sample-accurate; m4a loops are resampled to a multiple of 1024 samples so AAC decodes gapless.',assets=items)
m['mix_version']='v5'
json.dump(m,open(f'{root}/manifest.json','w'),indent=1,ensure_ascii=False)
REL='https://github.com/naraniwal007/nakshveda-sounds/releases/download/packs-v1/'
app=dict(m); app['assets']=[dict(a,file=os.path.basename(a['file']),path=a['file'],url=REL+os.path.basename(a['file'])) for a in items]
app['base_url']=REL
json.dump(app,open(f'{root}/manifest_app.json','w'),indent=1,ensure_ascii=False); print(len(items),'assets')
