"""Strict reader for the raw-payload JTMod v9 subset emitted here."""
import hashlib,struct
from pathlib import PurePosixPath
def u32(v):return struct.pack('<I',v)
def blob(v):
    if isinstance(v,str):v=v.encode('utf-8')
    return u32(len(v))+v
def seal(core):return core+b'JTMHASH1'+hashlib.sha256(b'jtmod-integrity-v1'+core).digest()
def unseal(data):
    assert data[-40:-32]==b'JTMHASH1' and hashlib.sha256(b'jtmod-integrity-v1'+data[:-40]).digest()==data[-32:]
    return data[:-40]
class Reader:
    def __init__(self,data):self.data=data;self.pos=0
    def take(self,n):
        assert 0<=n<=len(self.data)-self.pos
        value=self.data[self.pos:self.pos+n];self.pos+=n;return value
    def u32(self):return struct.unpack('<I',self.take(4))[0]
    def blob(self):return self.take(self.u32())
def read_v9(data):
    r=Reader(unseal(data));assert r.take(8)==b'JADEJTM1';assert r.u32()==9 and r.u32()==0
    game,archive,base=r.blob(),r.blob(),r.take(40)
    meta=[r.blob() for _ in range(6)];image=r.blob();keys=r.take(r.u32()*4)
    payloads=[]
    for _ in range(r.u32()):
        assert r.take(1)==b'\0';n=r.u32();assert r.u32()==n;payloads.append(r.take(n))
    count=r.u32();bins=[]
    for _ in range(count):
        entry=r.take(5);mode=entry[-1]
        if mode==1:
            entry+=r.take(36);n=r.u32();entry+=u32(n)
            for _ in range(n):
                entry+=r.take(8);m=r.u32();entry+=u32(m)
                for _ in range(m):entry+=blob(payloads[r.u32()])
        elif mode==2:entry+=blob(payloads[r.u32()])
        elif mode==3:entry+=blob(r.blob())+r.take(4)+blob(payloads[r.u32()])
        else:raise ValueError('Unexpected bin operation')
        bins.append(entry)
    files={};operations=[]
    for _ in range(r.u32()):
        mode=r.take(1)[0];assert mode in (3,7,8);path=r.blob().decode('utf-8')
        assert not PurePosixPath(path).is_absolute() and '..' not in PurePosixPath(path).parts and ':' not in path and '\\' not in path and path not in files
        external_archive,alias,original=r.blob(),r.blob(),r.blob()
        if mode==8:assert external_archive==alias==original==b''
        else:
            assert external_archive==b'soundlocal' and alias==b''
            assert (mode==7 and original==b'') or (mode==3 and len(original)==64)
        files[path]=payloads[r.u32()]
        operations.append({'mode':mode,'path':path,'archive':external_archive.decode(),'originalSha256':original.decode()})
    assert r.pos==len(r.data)
    model=b'JADEJTM1'+u32(3)+u32(0)+blob(game)+blob(archive)+base+b''.join(blob(v) for v in meta)+blob(image)+u32(len(keys)//4)+keys+u32(count)+b''.join(bins)
    return {'files':files,'operations':operations,'binCount':count,'modelV3':seal(model),'base':base,'metadata':meta,'bins':bins,'keys':keys}
