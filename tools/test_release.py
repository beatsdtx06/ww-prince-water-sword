"""Check release integrity; optional real-game COPY roundtrip (never edits inputs).

python tools/test_release.py --base-sound ORIGINAL.big --fat ORIGINAL.fat \
    --steam-archive APPLIED-STEAM.bf --openjade-archive APPLIED-OPENJADE.bf \
    --manager-exe LARGE-ASSETS-POP3.EXE --stock-exe STOCK-POP3.EXE
"""
import argparse
import hashlib
import json
from pathlib import Path
import shutil
import subprocess
import tempfile
from jtmod import read_v9, Reader, unseal, blob, u32
from package_release import PREFIX, MODEL_COMMIT, MODEL_FILE, build

ROOT = Path(__file__).resolve().parents[1]
SHELL = shutil.which("powershell.exe")
def sha(path):
    with path.open("rb") as stream:
        return hashlib.file_digest(stream, "sha256").hexdigest()

def run(script, *args, expect=0, contains=None):
    proc = subprocess.run([SHELL, "-NoProfile", "-ExecutionPolicy", "Bypass", "-File", str(script), *args],
                          capture_output=True, text=True)
    assert proc.returncode == expect, proc.stdout + proc.stderr
    if contains:
        assert ' '.join(contains.split()) in ' '.join((proc.stdout + proc.stderr).split()), proc.stdout + proc.stderr
    return proc

def main():
    parser = argparse.ArgumentParser()
    for name in ("base-sound", "fat", "steam-archive", "openjade-archive", "manager-exe", "stock-exe"):
        parser.add_argument("--" + name, type=Path)
    args = parser.parse_args()
    manifest = json.loads((ROOT / "package-manifest.json").read_text())
    for item in manifest["files"]:
        file = ROOT / item["path"]
        assert file.stat().st_size == item["bytes"] and sha(file) == item["sha256"], item["path"]
    for line in (ROOT / "SHA256SUMS.txt").read_text().splitlines():
        digest, path = line.split("  ", 1)
        assert sha(ROOT / path) == digest
    archive = ROOT / "assets/WW-Prince-Model-Sword-Voice-0.5.0.jtmod"
    decoded=read_v9(archive.read_bytes())
    model=subprocess.check_output(['git','show',MODEL_COMMIT+':'+MODEL_FILE],cwd=ROOT)
    r=Reader(unseal(model));r.take(16);r.blob();r.blob();base=r.take(40)
    for _ in range(7):r.blob()
    r.take(r.u32()*4);count=r.u32()
    assert base==decoded['base'] and count==decoded['binCount']
    assert r.take(len(r.data)-r.pos)==b''.join(decoded['bins']), 'Native BF edits changed'
    assert build(model,{k.removeprefix(PREFIX):v for k,v in decoded['files'].items()})==archive.read_bytes()
    catalog=json.loads((ROOT/'pmm_manifest.json').read_text())['mods']
    assert len(catalog)==1 and catalog[0]['targets']=='both' and catalog[0]['sha256']==sha(archive)
    with tempfile.TemporaryDirectory(prefix="ww-bundle-test-") as tmp:
        scratch = Path(tmp)
        names=list(decoded['files'])
        assert len(names)==len(manifest['files'])+1
        assert all(n.startswith(PREFIX) for n in names)
        assert not any(n.endswith(('.exe','.dll','.big','.bf','.wav','.pt','.pth')) for n in names)
        for name,data in decoded['files'].items():
            file=scratch/name;file.parent.mkdir(parents=True,exist_ok=True);file.write_bytes(data)
        package = scratch / PREFIX
        for item in manifest["files"]:
            assert sha(package / item["path"]) == item["sha256"]
        voice = json.loads((package / "voice/manifest.json").read_text())
        assert len(voice["patches"]) == 93 and len(voice["heldSpokenIndices"]) == 17
        assert not set(voice["heldSpokenIndices"]) & {p["index"] for p in voice["patches"]}
        for path in package.rglob("*"):
            if path.is_file() and path.suffix in {".md", ".json", ".ps1", ".cmd", ".txt"}:
                content = path.read_text(encoding="utf-8-sig")
                assert "C:\\Users\\" not in content and "C:/Users/" not in content
                assert "sk-proj-" not in content
        print("PASS: single JTMod integrity/inventory, unchanged BF edits, deterministic encoding, all hashes, 93 payloads, held exclusion, private-path/credential-marker scan", flush=True)
        if not any(vars(args).values()):
            return
        assert all(vars(args).values()), "Supply all six real-archive inputs together."
        assert sha(args.base_sound) == voice["baseSha256"]
        assert sha(args.fat) == voice["fatSha256"]
        for edition, model in (("Steam", args.steam_archive), ("OpenJade", args.openjade_archive)):
            game = scratch / edition
            (game / "Sound").mkdir(parents=True)
            shutil.copy2(args.base_sound, game / "Sound/soundlocal.big")
            shutil.copy2(args.fat, game / "Sound/soundlocal.fat")
            shutil.copy2(args.steam_archive, game / "pop3.bf")
            installed_package=game/PREFIX
            shutil.copytree(package,installed_package)
            if edition == "Steam":
                shutil.copy2(args.manager_exe, game / "POP3.EXE")
                shutil.copy2(args.stock_exe, game / "POP3.EXE.popmm.bak")
            launcher = installed_package / "Manage-Mod.ps1"
            parameters = ("-Edition", edition)
            run(launcher, "-Action", "Check", *parameters, expect=2, contains="not fully installed")
            run(launcher, "-Action", "Install", *parameters, contains="93-line voice preview installed")
            run(launcher, "-Action", "Check", *parameters, contains="All three components match")
            assert sha(game/'pop3.bf')==sha(model)
            assert sha(game / "Sound/soundlocal.big") == voice["patchedSha256"]
            original = args.base_sound.read_bytes()
            patched = (game / "Sound/soundlocal.big").read_bytes()
            cursor = 0
            for patch in sorted(voice["patches"], key=lambda p:p["start"]):
                start, end = patch["start"], patch["start"] + patch["length"]
                assert original[cursor:start] == patched[cursor:start]
                assert patched[start:end] == (package / "voice" / patch["file"]).read_bytes()
                cursor = end
            assert original[cursor:] == patched[cursor:]
            run(launcher, "-Action", "Install", *parameters)
            run(launcher, "-Action", "Restore", *parameters)
            run(launcher, "-Action", "Restore", *parameters)
            assert sha(game / "Sound/soundlocal.big") == voice["baseSha256"]
            assert sha(game / "Sound/soundlocal.fat") == voice["fatSha256"]
            assert sha(game / "pop3.bf") == sha(args.steam_archive)
            if edition == "Steam":
                assert sha(game / "POP3.EXE") == sha(args.manager_exe)
            else:
                helper=installed_package/'installers/Manage-OpenJade-Effects.ps1'
                backup=game/'WWPrinceEffectsBackup/pop3.bf.before-openjade-effects'
                backup.write_bytes(b'corrupt test backup')
                run(helper,'-Action','Install','-GameDirectory',str(game),expect=1,contains='Existing effects backup does not match')
                assert sha(game/'pop3.bf')==sha(args.steam_archive)
                shutil.copy2(args.steam_archive,backup)
                delta=installed_package/'installers/openjade-effects.delta.gz'
                saved=delta.read_bytes();delta.write_bytes(b'bad gzip fixture')
                run(helper,'-Action','Install','-GameDirectory',str(game),expect=1)
                assert sha(game/'pop3.bf')==sha(args.steam_archive)
                assert sha(backup)==sha(args.steam_archive)
                assert not (backup.parent/'pop3.bf.effects.tmp').exists()
                delta.write_bytes(saved)
                print('PASS: OpenJade corrupt backup/delta refused without changing archive',flush=True)
            # Refuse the wrong model without touching the voice archive.
            (game / "pop3.bf").write_bytes(b"unsupported model fixture")
            run(launcher, "-Action", "Install", *parameters, expect=1, contains="Apply the universal")
            assert sha(game / "Sound/soundlocal.big") == voice["baseSha256"]
            print(f"PASS: {edition} extracted-bundle install/check/repeat/restore, unchanged outside ranges, wrong-model refusal", flush=True)
        # Package tampering is detected before touching any game component.
        (package / "voice/patches/270.bin").write_bytes(b"corrupt")
        run(package / "Manage-Mod.ps1", "-Action", "Install", "-Edition", "OpenJade",
            "-GameDirectory", str(scratch / "OpenJade"), expect=1, contains="Changed bundle file")
        print("PASS: corrupted bundle refused before installation", flush=True)

if __name__ == "__main__":
    main()
