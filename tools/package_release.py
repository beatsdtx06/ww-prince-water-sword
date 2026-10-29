"""Reproducible single JTMod v9 with model edits and bounded added setup files."""
import argparse, hashlib, json, subprocess
from pathlib import Path
from jtmod import Reader, blob, u32, seal, read_v9, unseal
ROOT=Path(__file__).resolve().parents[1]
NAME='WW-Prince-Model-Sword-Voice-0.5.0'
PREFIX='WWPrince-Model-Sword-Voice/'
MODEL_COMMIT='649046bac415656de88d1198e4ae3b25013c057d'
MODEL_FILE='WW-Prince-Water-Sword-Steam-Clean-Start-0.4.0.jtmod'
MODEL_SHA='faa674ce17ba785c1d6e9bc7d3122732b722a8d8a7ebf53a066f982c2b5b1d29'
def sha(path):return hashlib.sha256(path.read_bytes()).hexdigest()
def runtime_files():
    paths=[ROOT/n for n in ('Finish-Setup.cmd','Manage-Mod.cmd','Manage-Mod.ps1','README.md','NOTICES.md','CHANGELOG.md')]
    for folder,exts in {'installers':{'.ps1','.gz'},'voice':{'.ps1','.json','.bin'},'docs':{'.md','.json'}}.items():
        for path in sorted((ROOT/folder).rglob('*')):
            if path.is_file():
                assert not path.is_symlink() and path.suffix in exts,path
                paths.append(path)
    paths.append(ROOT/'assets/steam-gameplay.jpg')
    return sorted(paths,key=lambda p:p.relative_to(ROOT).as_posix())
def build(model,files):
    assert hashlib.sha256(model).hexdigest()==MODEL_SHA
    r=Reader(unseal(model));assert r.take(8)==b'JADEJTM1';assert r.u32()==3 and r.u32()==0
    game,archive,base=r.blob(),r.blob(),r.take(40)
    metadata=[r.blob() for _ in range(6)];image=r.blob();keys=r.take(r.u32()*4)
    payloads=[];indices={}
    def ref(data):
        digest=hashlib.sha256(data).digest()
        if digest not in indices:indices[digest]=len(payloads);payloads.append(data)
        return u32(indices[digest])
    bins=[]
    for _ in range(r.u32()):
        head=r.take(5);mode=head[-1];entry=head
        if mode==1:
            entry+=r.take(36);count=r.u32();entry+=u32(count)
            for _ in range(count):
                entry+=r.take(8);n=r.u32();entry+=u32(n)
                for _ in range(n):entry+=ref(r.blob())
        elif mode==2:entry+=ref(r.blob())
        elif mode==3:entry+=blob(r.blob())+r.take(4)+ref(r.blob())
        else:raise ValueError('Unknown bin mode')
        bins.append(entry)
    assert r.pos==len(r.data)
    metadata[0]=b'WW Prince - Model, Water Sword and Voice';metadata[2]=b'0.5.0'
    metadata[3]=b'One package for Steam and OpenJade 0.4.1. WW Prince, clean-start Water Sword and 93-line English AI voice preview. After Apply, close the game and manager, run WWPrince-Model-Sword-Voice/Finish-Setup.cmd inside the game folder. Select your edition: OpenJade keeps enhanced damage and boss blue aura; Steam requires Large assets and the included interpreter fix. Do not stack with older editions or overlapping mods. See included README.'
    metadata[4]=b'2026-10-29T00:00:00Z';metadata[5]=b'WW universal packager 0.5.0'
    ops=[]
    for path,data in sorted(files.items()):ops.append(b'\x08'+blob(PREFIX+path)+blob('')+blob('')+blob('')+ref(data))
    core=b'JADEJTM1'+u32(9)+u32(0)+blob(game)+blob(archive)+base
    core+=b''.join(blob(v) for v in metadata)+blob(image)+u32(len(keys)//4)+keys
    core+=u32(len(payloads))+b''.join(b'\0'+u32(len(p))+u32(len(p))+p for p in payloads)
    core+=u32(len(bins))+b''.join(bins)+u32(len(ops))+b''.join(ops)
    return seal(core)
def main():
    p=argparse.ArgumentParser();p.add_argument('--model-input',type=Path);args=p.parse_args()
    model=args.model_input.read_bytes() if args.model_input else subprocess.check_output(['git','show',MODEL_COMMIT+':'+MODEL_FILE],cwd=ROOT)
    paths=runtime_files();voice=json.loads((ROOT/'voice/manifest.json').read_text())
    assert len(voice['patches'])==93
    assert {ROOT/'voice'/p['file'] for p in voice['patches']}==set((ROOT/'voice/patches').glob('*.bin'))
    for patch in voice['patches']:
        file=ROOT/'voice'/patch['file'];assert file.stat().st_size==patch['length'] and sha(file)==patch['sha256']
    manifest={'name':NAME,'version':'0.5.0','voicePreview':True,'voiceLines':93,'files':[{'path':x.relative_to(ROOT).as_posix(),'bytes':x.stat().st_size,'sha256':sha(x)} for x in paths]}
    metadata=ROOT/'package-manifest.json';metadata.write_text(json.dumps(manifest,indent=2)+'\n',encoding='utf-8',newline='\n')
    paths.append(metadata);files={x.relative_to(ROOT).as_posix():x.read_bytes() for x in paths}
    result=build(model,files);decoded=read_v9(result)
    assert decoded['files']=={PREFIX+k:v for k,v in files.items()}
    out=ROOT/'assets'/(NAME+'.jtmod');out.write_bytes(result)
    catalog={'mods':[{'id':'ww-prince-model-sword-voice','name':'WW Prince - Model, Water Sword and Voice','author':'beatsdtx06','version':'0.5.0','description':'One JTMod for Steam and OpenJade 0.4.1. Apply, then run the included Finish-Setup.cmd inside the game folder. Model + New Game Water Sword + 93-line English AI voice preview. OpenJade retains enhanced damage and boss-only blue aura. Steam needs Large assets. Clean base required; replaces older separate editions.','file':'assets/'+out.name,'game':'T2T','type':'mod','targets':'both','size':len(result),'sha256':sha(out),'image':'assets/steam-gameplay.jpg'}]}
    (ROOT/'pmm_manifest.json').write_text(json.dumps(catalog,indent=2)+'\n',encoding='utf-8',newline='\n')
    (ROOT/'SHA256SUMS.txt').write_text(f'{sha(out)}  assets/{out.name}\n',encoding='utf-8',newline='\n')
    print(json.dumps({'file':out.name,'bytes':len(result),'sha256':sha(out),'embeddedFiles':len(files),'modelBins':decoded['binCount']}))
if __name__=='__main__':main()
