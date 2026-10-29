"""Independent structural/content checks for the native OpenJade release."""
import argparse
import hashlib
import json
import struct
import subprocess
import tempfile
import zipfile
from pathlib import Path
from jtmod import Reader, read_v9, unseal
from package_release import NAME, MODEL_COMMIT, MODEL_FILE, MODEL_SHA, BANK_SHA, BANK_OUT_SHA, STREAM_SHA, audio

ROOT=Path(__file__).resolve().parents[1]
def sha(data):return hashlib.sha256(data).hexdigest()

def model_body(data):
    r=Reader(unseal(data));assert r.take(8)==b'JADEJTM1' and r.u32()==3 and r.u32()==0
    game,archive,base=r.blob(),r.blob(),r.take(40)
    for _ in range(7):r.blob()
    keys=r.take(r.u32()*4)
    return game,archive,base,keys,r.data[r.pos:]

def sound_entries(folder,stem):
    fat=(folder/(stem+'.fat')).read_bytes();big=(folder/(stem+'.big')).read_bytes()
    out={};pos=0
    while pos<len(fat):
        prev,offset,size,flags,length=struct.unpack_from('<5I',fat,pos)
        name=fat[pos+20:pos+20+length].rstrip(b'\0').decode().replace('\\','/').lower()
        assert name not in out and offset+size<=len(big)
        out[name]=big[offset:offset+size];pos+=20+length
    assert pos==len(fat)
    return out

def main():
    p=argparse.ArgumentParser()
    p.add_argument('--bank',type=Path)
    p.add_argument('--game',type=Path)
    p.add_argument('--banks',type=Path,help='Extracted original bank directory with bank-index.json')
    p.add_argument('--decoder',type=Path)
    p.add_argument('--report',type=Path)
    args=p.parse_args()
    artifact=ROOT/'assets'/(NAME+'.jtmod');data=artifact.read_bytes();decoded=read_v9(data)
    model=subprocess.check_output(['git','show',MODEL_COMMIT+':'+MODEL_FILE],cwd=ROOT)
    assert sha(model)==MODEL_SHA
    assert model_body(decoded['modelV3'])==model_body(model), 'Accepted model/effects records changed'
    assert decoded['metadata'][2]==b'0.5.1' and b'OpenJade' in decoded['metadata'][0]
    assert [o['mode'] for o in decoded['operations']]==[7,3]
    assert decoded['operations'][1]['originalSha256']==BANK_SHA
    assert set(decoded['files'])=={'sound/english/001.sb0','sound/english/wwprince.ls0'}
    bank=decoded['files']['sound/english/001.sb0'];stream=decoded['files']['sound/english/wwprince.ls0']
    assert sha(bank)==BANK_OUT_SHA and sha(stream)==STREAM_SHA
    records=json.loads((ROOT/'source/voice-record-map.json').read_text())['records']
    patches=json.loads((ROOT/'voice/manifest.json').read_text())['patches']
    assert len(records)==len(patches)==93
    held={259,275,280,289,300,304,307,314,316,318,320,321,323,344,348,351,358,257,258,*range(367,378)}
    assert not held.intersection(p['index'] for p in patches)
    version,n1,n2,n3,extra_size=struct.unpack_from('<5I',bank)
    sec2=28+n1*0x68;extra=sec2+n2*0x78;cursor=0
    for row,patch in zip(records,patches):
        assert row['index']==patch['index'] and row['streamOffset']==cursor
        pos=sec2+row['row']*0x78
        offset=struct.unpack_from('<I',bank,pos+0x10)[0]
        filename=struct.unpack_from('<I',bank,pos+0x64)[0]
        assert offset==cursor and bank[extra+filename:].split(b'\0',1)[0]==b'WWPRINCE.LS0'
        content=stream[cursor:cursor+patch['length']]
        assert sha(content)==patch['sha256'] and content==(ROOT/'voice'/patch['file']).read_bytes()
        cursor+=patch['length']
    assert cursor==len(stream)
    if args.bank:
        original=args.bank.read_bytes()
        assert audio(original,records,patches)==(bank,stream)
        corrupt=bytearray(original);corrupt[-1]^=1
        try:audio(corrupt,records,patches)
        except AssertionError:pass
        else:raise AssertionError('Wrong bank accepted')
    tampered=bytearray(data);tampered[100]^=1
    try:read_v9(tampered)
    except AssertionError:pass
    else:raise AssertionError('Corrupt package accepted')
    catalog=json.loads((ROOT/'pmm_manifest.json').read_text())['mods']
    assert len(catalog)==1 and catalog[0]['targets']=='openjade'
    assert catalog[0]['sha256']==sha(data) and catalog[0]['size']==len(data)
    manifest=json.loads((ROOT/'package-manifest.json').read_text())
    assert manifest['jtmod']['sha256']==sha(data) and not manifest['scriptsRequired']
    assert manifest['modelBins']==decoded['binCount']
    with zipfile.ZipFile(ROOT/'assets'/(NAME+'.zip')) as z:
        assert set(z.namelist())=={artifact.name,'README.txt','NOTICES.txt','SHA256SUMS.txt'}
        assert z.read(artifact.name)==data and z.testzip() is None
        assert z.read('SHA256SUMS.txt').decode()==sha(data)+'  '+artifact.name+'\n'
    for line in (ROOT/'SHA256SUMS.txt').read_text().splitlines():
        expected,path=line.split('  ');assert sha((ROOT/path).read_bytes())==expected
    report={'status':'NATIVE_RELEASE_STRUCTURE_PASS','version':'0.5.1','target':'openjade',
        'packageSha256':sha(data),'modelRecordsExact':True,'approvedClipsExact':93,
        'nativeAudioOperations':[7,3],'setupScriptsRequired':False,'executableFiles':0,
        'zipSingleJtmod':True,'installedCopyChecked':False,'decodedAllClips':False}
    if args.game:
        assert args.banks,'--game requires --banks for independent original asset comparisons'
        assert sha((args.game/'pop3.bf').read_bytes())==manifest['modelAppliedSha256']
        installed={}
        for stem in ('sound','soundlocal'):installed.update(sound_entries(args.game/'Sound',stem))
        index=json.loads((args.banks/'bank-index.json').read_text())
        assert set(installed)=={r['name'].lower() for r in index}|{'sound/english/wwprince.ls0'}
        for row in index:
            name=row['name'].lower()
            if name!='sound/english/001.sb0':assert sha(installed[name])==row['sha256'],name
        for name,content in decoded['files'].items():assert installed[name]==content
        assert not (args.game/'WWPrince-Model-Sword-Voice').exists()
        report.update(installedCopyChecked=True,otherSoundAssetsExact=len(index)-1)
    if args.decoder:
        with tempfile.TemporaryDirectory(prefix='ww-native-decode-') as tmp:
            stage=Path(tmp);(stage/'001.sb0').write_bytes(bank);(stage/'WWPRINCE.LS0').write_bytes(stream)
            for record in records:
                decoded_audio=subprocess.run([str(args.decoder),'-p','-s',str(record['index']),str(stage/'001.sb0')],stdout=subprocess.PIPE,stderr=subprocess.PIPE,check=True)
                assert decoded_audio.stdout[:4]==b'RIFF' and len(decoded_audio.stdout)>44,record['index']
            report['decodedAllClips']=True
    if args.report:args.report.write_text(json.dumps(report,indent=2)+'\n',encoding='utf-8')
    print(json.dumps(report))

if __name__=='__main__':main()
