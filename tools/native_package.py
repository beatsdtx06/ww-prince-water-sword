"""Encode unchanged v3 model records and native sound operations as JTMod v9."""
import hashlib
from jtmod import Reader, blob, u32, seal, unseal

def native_package(model, stream, bank, bank_sha, release=True):
    assert release, 'Only the final OpenJade release is supported'
    r=Reader(unseal(model))
    assert r.take(8)==b'JADEJTM1' and r.u32()==3 and r.u32()==0
    game,archive,base=r.blob(),r.blob(),r.take(40)
    metadata=[r.blob() for _ in range(6)]
    picture,keys=r.blob(),r.take(r.u32()*4)
    payloads,lookup=[],{}
    def ref(data):
        digest=hashlib.sha256(data).digest()
        if digest not in lookup:
            lookup[digest]=len(payloads);payloads.append(data)
        return u32(lookup[digest])
    bins=[]
    for _ in range(r.u32()):
        entry=r.take(5);mode=entry[-1]
        if mode==1:
            entry+=r.take(36);count=r.u32();entry+=u32(count)
            for _ in range(count):
                entry+=r.take(8);count=r.u32();entry+=u32(count)
                for _ in range(count):entry+=ref(r.blob())
        elif mode==2:entry+=ref(r.blob())
        elif mode==3:entry+=blob(r.blob())+r.take(4)+ref(r.blob())
        else:raise ValueError('Unknown model operation')
        bins.append(entry)
    assert r.pos==len(r.data)
    metadata[0]=b'WW Prince - Model, Water Sword and Voice (OpenJade)'
    metadata[2]=b'0.5.1'
    metadata[3]=b'OpenJade 0.5.1 ONLY. WW Prince model, Water Sword from New Game, enhanced damage and boss-only blue aura, plus the approved 93-line English AI voice preview. Import and Apply in PoP Mod Manager 2.1.2, then launch. No setup scripts or extra installer. Disable older WW Prince packages; do not stack editions. Steam is not supported.'
    metadata[4]=b'2026-10-29T00:00:00Z'
    metadata[5]=b'OpenJade native packager 0.5.1'
    ops=[b'\x07'+blob('sound/english/wwprince.ls0')+blob('soundlocal')+blob('')+blob('')+ref(stream),
         b'\x03'+blob('sound/english/001.sb0')+blob('soundlocal')+blob('')+blob(bank_sha)+ref(bank)]
    core=b'JADEJTM1'+u32(9)+u32(0)+blob(game)+blob(archive)+base
    core+=b''.join(blob(m) for m in metadata)+blob(picture)+u32(len(keys)//4)+keys
    core+=u32(len(payloads))+b''.join(b'\0'+u32(len(p))+u32(len(p))+p for p in payloads)
    core+=u32(len(bins))+b''.join(bins)+u32(len(ops))+b''.join(ops)
    return seal(core)
