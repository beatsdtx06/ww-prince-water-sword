"""Build a hash-guarded copy/literal delta, never a complete game archive."""
import argparse, gzip, hashlib, json, subprocess, tempfile
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
BASE = 'cb9424bf647d6a3eac08ab139dbc68ae4024378ef43c43f00f18c8ab8a1c4644'
TARGET = '3d4b138b0babfe026669db584b5bed29b25ddca94f23172cfa6c30f288c3409d'

def main():
    p=argparse.ArgumentParser(); p.add_argument('steam',type=Path); p.add_argument('openjade',type=Path); p.add_argument('--encoder',required=True,type=Path); args=p.parse_args()
    base=args.steam.read_bytes(); target=args.openjade.read_bytes()
    assert hashlib.sha256(base).hexdigest()==BASE
    assert hashlib.sha256(target).hexdigest()==TARGET
    del base,target
    out=ROOT/'installers/openjade-effects.delta.gz'
    with tempfile.TemporaryDirectory(prefix='ww-effects-delta-') as tmp:
        raw=Path(tmp)/'delta.raw'
        subprocess.run([str(args.encoder),str(args.steam),str(args.openjade),str(raw)],check=True)
        out.write_bytes(gzip.compress(raw.read_bytes(),compresslevel=9,mtime=0))
    print(json.dumps({'file':out.name,'bytes':out.stat().st_size,'sha256':hashlib.sha256(out.read_bytes()).hexdigest()}))

if __name__=='__main__':main()
