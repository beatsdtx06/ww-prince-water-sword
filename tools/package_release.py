"""Build a deterministic OpenJade-only native JTMod and player ZIP.

Requires the user's original English 001.sb0; never edits a game installation.
The historical model input is kept in Git, not duplicated among player downloads.
"""
import argparse
import hashlib
import json
import struct
import subprocess
import zipfile
from pathlib import Path
from jtmod import read_v9
from native_package import native_package

ROOT = Path(__file__).resolve().parents[1]
NAME = 'WW-Prince-Model-Sword-Voice-0.5.1'
MODEL_COMMIT = '649046bac415656de88d1198e4ae3b25013c057d'
MODEL_FILE = 'WW-Prince-Water-Sword-OpenJade-Clean-Start-0.4.0.jtmod'
MODEL_SHA = 'b579b7b61a8fb69d0785b636b1b8422918b9b495295d1a814d480aceca410bf0'
BANK_SHA = 'a83de99c058b688e07c944cb97cb1a1dbb2736eefd3486196865afff5db8a3a0'
BANK_OUT_SHA = 'efbe9ce1441782f0d23804ef79619755426dd1072b78dd8fbfb75491a2ed24d3'
STREAM_SHA = '8b2db59b6765d6e0a3019551496991320335b7e67a37558bcbefaefd2ed16315'

def digest(data):
    return hashlib.sha256(data).hexdigest()

def dump(path, value):
    path.write_text(json.dumps(value, indent=2)+'\n', encoding='utf-8', newline='\n')

def audio(bank_original, records, patches):
    assert digest(bank_original) == BANK_SHA, 'Unsupported original English bank'
    bank = bytearray(bank_original)
    version, n1, n2, n3, extra_size = struct.unpack_from('<5I', bank)
    assert version == 0x00150000
    start2 = 28+n1*0x68
    extra = start2+n2*0x78
    end = extra+extra_size
    name = b'WWPRINCE.LS0\0'.ljust(40,b'\0')
    bank[end:end] = name
    struct.pack_into('<I',bank,16,extra_size+len(name))
    stream = bytearray()
    changed = set()
    assert len(records)==len(patches)==93
    for record, patch in zip(records,patches):
        assert record['index']==patch['index'] and record['row'] not in changed
        assert 0 <= record['row'] < n2
        changed.add(record['row'])
        pos = start2+record['row']*0x78
        ident,kind,length,unused,old_offset = struct.unpack_from('<5I',bank,pos)
        assert kind==1 and length==patch['length']==record['length']
        assert old_offset+12815346==patch['start']
        old_name = struct.unpack_from('<I',bank,pos+0x64)[0]
        assert bank_original[extra+old_name:].split(b'\0',1)[0].lower()==b'stream.ls0'
        data = (ROOT/'voice'/patch['file']).read_bytes()
        assert len(data)==length and digest(data)==patch['sha256']
        assert len(stream)==record['streamOffset']
        struct.pack_into('<I',bank,pos+0x10,len(stream))
        struct.pack_into('<I',bank,pos+0x64,extra_size)
        stream.extend(data)
    for row in range(n2):
        if row not in changed:
            pos=start2+row*0x78
            assert bank[pos:pos+0x78]==bank_original[pos:pos+0x78]
    assert bank[extra:end]==bank_original[extra:end]
    assert bank[end+40:]==bank_original[end:]
    assert digest(bank)==BANK_OUT_SHA and digest(stream)==STREAM_SHA
    return bytes(bank),bytes(stream)

def main():
    parser=argparse.ArgumentParser()
    parser.add_argument('--bank',required=True,type=Path)
    parser.add_argument('--model-input',type=Path)
    parser.add_argument('--record-map-from-probe',type=Path,help='One-time developer migration from verified probe report')
    args=parser.parse_args()
    if args.record_map_from_probe:
        probe=json.loads(args.record_map_from_probe.read_text())
        assert probe['bankSha256']==BANK_OUT_SHA and probe['streamSha256']==STREAM_SHA
        dump(ROOT/'source/voice-record-map.json',{'format':1,'records':probe['records']})
    records=json.loads((ROOT/'source/voice-record-map.json').read_text())['records']
    voice=json.loads((ROOT/'voice/manifest.json').read_text())
    patches=voice['patches']
    assert {p['file'] for p in patches}=={'patches/'+p.name for p in (ROOT/'voice/patches').glob('*.bin')}
    bank,stream=audio(args.bank.read_bytes(),records,patches)
    model=args.model_input.read_bytes() if args.model_input else subprocess.check_output(['git','show',MODEL_COMMIT+':'+MODEL_FILE],cwd=ROOT)
    assert digest(model)==MODEL_SHA
    result=native_package(model,stream,bank,BANK_SHA,release=True)
    decoded=read_v9(result)
    assert [op['mode'] for op in decoded['operations']]==[7,3]
    assert decoded['files']=={'sound/english/wwprince.ls0':stream,'sound/english/001.sb0':bank}
    out=ROOT/'assets'/(NAME+'.jtmod')
    out.parent.mkdir(parents=True,exist_ok=True)
    out.write_bytes(result)
    manifest={'version':'0.5.1','target':'openjade','engineTested':'0.5.1','jtmodVersion':9,
        'scriptsRequired':False,'executableFiles':0,'voiceLines':93,'modelSourceSha256':MODEL_SHA,
        'modelBins':decoded['binCount'],'modelAppliedSha256':'3d4b138b0babfe026669db584b5bed29b25ddca94f23172cfa6c30f288c3409d',
        'operations':[dict(op,bytes=len(decoded['files'][op['path']]),sha256=digest(decoded['files'][op['path']])) for op in decoded['operations']],
        'jtmod':{'file':'assets/'+out.name,'bytes':len(result),'sha256':digest(result)}}
    dump(ROOT/'package-manifest.json',manifest)
    item={'id':'ww-prince-model-sword-voice','name':'WW Prince - Model, Water Sword and Voice (OpenJade)',
        'author':'beatsdtx06','version':'0.5.1','description':decoded['metadata'][3].decode(),
        'file':'assets/'+out.name,'game':'T2T','type':'mod','targets':'openjade','size':len(result),'sha256':digest(result)}
    dump(ROOT/'pmm_manifest.json',{'mods':[item]})
    readme=('WW PRINCE - MODEL, WATER SWORD & VOICE 0.5.1\nOPENJADE ONLY - NOT ORIGINAL STEAM ENGINE\n\n'
        'Requires an existing OpenJade 0.5.1 game with supported English audio and PoP Mod Manager 2.1.2.\n'
        '1. Extract this ZIP.\n2. Import '+out.name+' into Mod Manager for OpenJade The Two Thrones.\n'
        '3. Disable older WW Prince/model/sword/voice packages. Enable this one and Apply.\n4. Launch the game.\n\n'
        'No CMD, PowerShell, installer, executable patch, or extra setup.\n'
        'Includes WW Prince model, clean-start Water Sword, enhanced damage, boss-only blue aura,\n'
        'and 93 approved English AI-converted spoken lines. Voice coverage is partial.\n'
        'Back up saves. Other language banks and overlapping sound/model mods are not supported.\n'
        'Use Mod Manager Restore original to uninstall; its backups must be retained.\n'
        'If you previously RAN the old 0.5.0 helper, see the repository recovery guide before upgrading.\n\n'
        'https://github.com/beatsdtx06/ww-prince-water-sword\n')
    zip_path=ROOT/'assets'/(NAME+'.zip')
    contents={out.name:result,'README.txt':readme.encode(),'NOTICES.txt':(ROOT/'NOTICES.md').read_bytes(),
        'SHA256SUMS.txt':(digest(result)+'  '+out.name+'\n').encode()}
    with zipfile.ZipFile(zip_path,'w',compression=zipfile.ZIP_DEFLATED,compresslevel=9) as z:
        for name,data in sorted(contents.items()):
            entry=zipfile.ZipInfo(name,(2026,10,29,0,0,0));entry.compress_type=zipfile.ZIP_DEFLATED
            entry.external_attr=0o100644<<16
            z.writestr(entry,data,compresslevel=9)
    (ROOT/'SHA256SUMS.txt').write_text(''.join(digest(p.read_bytes())+'  assets/'+p.name+'\n' for p in (out,zip_path)),encoding='utf-8',newline='\n')
    print(json.dumps({'jtmod':manifest['jtmod'],'zip':{'file':zip_path.name,'bytes':zip_path.stat().st_size,'sha256':digest(zip_path.read_bytes())}}))

if __name__=='__main__':main()
