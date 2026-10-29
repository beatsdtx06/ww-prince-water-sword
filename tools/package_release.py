"""Verify and repackage the existing approved 0.6.0 JTMod; never regenerate voices.

Only Python's standard library is required. No original game/audio files, API,
or local developer paths are required. Existing files are never overwritten.
"""
import argparse
import hashlib
import json
from pathlib import Path, PurePosixPath
import re
import zipfile

from jtmod import read_v9, model_fingerprint, require

ROOT = Path(__file__).resolve().parents[1]
RELEASE_URL = 'https://github.com/beatsdtx06/ww-prince-water-sword/releases/download/v0.6.0/'
COUNTS = dict(isolatedDialogueClips=110, inEngineSceneTracks=38,
              mappedScenePrinceTurns=80, nativeEffortResources=28,
              nativeResidentEffortResources=26, nativeDeathFallResources=2)
EXCLUSIONS = ['prerendered-videos', 'dark-prince', 'other-speakers']
OPERATIONS = [
    (7, 'sound/english/wwprince.ls0', ''),
    (3, 'sound/english/001.sb0', 'a83de99c058b688e07c944cb97cb1a1dbb2736eefd3486196865afff5db8a3a0'),
    (3, 'sound/english/004.sb0', '344c400ab5d051501ed5af25d19721f2b871fbc0cf13a263639c205c6ea0bc68'),
]


def digest(data):
    return hashlib.sha256(data).hexdigest()


def read_json(path):
    return json.loads(path.read_text(encoding='utf-8'))


def safe_relative(root, value):
    require(isinstance(value, str), 'Expected a relative path')
    path = PurePosixPath(value)
    require(value and not path.is_absolute() and '..' not in path.parts and ':' not in value
            and '\\' not in value and str(path) == value, 'Unsafe repository path')
    resolved = (root / value).resolve()
    require(resolved.is_relative_to(root.resolve()), 'Path escapes repository')
    return resolved


def verified_inputs(root, artifact):
    manifest = read_json(root / 'package-manifest.json')
    require(manifest.get('version') == '0.6.0' and manifest.get('target') == 'openjade'
            and manifest.get('jtmodVersion') == 9, 'This tool handles the approved OpenJade 0.6.0 release only')
    require(manifest.get('coverageCounts') == COUNTS, 'Unexpected coverage declaration')
    require(manifest.get('intentionalExclusions') == EXCLUSIONS, 'Missing intentional exclusions')
    require(manifest.get('scriptsRequired') is False and manifest.get('executableFiles') == 0,
            'Helpers/executables are not part of this release')
    require(manifest.get('modelBins') == 61, 'Unexpected model operation count')
    jtmod = manifest['jtmod']
    expected_name = 'WW-Prince-Model-Sword-Voice-0.6.0.jtmod'
    require(jtmod['file'] == expected_name and jtmod.get('downloadUrl') == RELEASE_URL + expected_name,
            'Unexpected JTMod release-asset identity')
    require(artifact is not None, 'Pass --artifact with the downloaded release ZIP or JTMod')
    artifact = Path(artifact)
    require(artifact.is_file(), 'Downloaded artifact does not exist: ' + str(artifact))
    archive_input = artifact.suffix.lower() == '.zip'
    if archive_input:
        zip_record = manifest['zip']
        expected_zip = 'WW-Prince-Model-Sword-Voice-0.6.0.zip'
        require(zip_record['file'] == expected_zip and zip_record.get('downloadUrl') == RELEASE_URL + expected_zip,
                'Unexpected ZIP release-asset identity')
        require(artifact.stat().st_size == zip_record['bytes'] and digest(artifact.read_bytes()) == zip_record['sha256'],
                'Downloaded ZIP hash/size mismatch')
        with zipfile.ZipFile(artifact) as archive:
            require(sorted(archive.namelist()) == sorted([expected_name,'README.txt','NOTICES.txt','SHA256SUMS.txt']),
                    'Unexpected or duplicate downloaded ZIP members')
            require(archive.testzip() is None, 'Downloaded ZIP CRC failed')
            package = archive.read(expected_name)
    else:
        require(artifact.suffix.lower() == '.jtmod', 'Artifact must be a release ZIP or JTMod')
        package = artifact.read_bytes()
    require(re.fullmatch('[0-9a-f]{64}', str(jtmod.get('sha256'))) is not None
            and digest(package) == jtmod['sha256'] and len(package) == jtmod['bytes'], 'JTMod hash/size mismatch')
    decoded = read_v9(package)
    require(decoded['game'] == b'T2T' and decoded['archive'] == b'pop3.bf', 'Wrong game/archive')
    require(decoded['metadata'][2] == b'0.6.0' and decoded['metadata'][1] == b'beatsdtx06', 'Wrong package metadata')
    require(decoded['binCount'] == 61, 'Wrong model operation count')
    require(model_fingerprint(decoded) == manifest.get('modelPayloadSha256'), 'Model prerequisite/operation hash mismatch')
    ops = decoded['operations']
    require([(op['mode'], op['path'], op['originalSha256']) for op in ops] == OPERATIONS,
            'Unexpected native operations, ordering or original hash guards')
    actual = [dict(op, bytes=len(decoded['files'][op['path']]),
                   sha256=digest(decoded['files'][op['path']])) for op in ops]
    require(actual == manifest.get('operations'), 'Native payload manifest mismatch')
    pmm = read_json(root / 'pmm_manifest.json')
    require(pmm == {'mods': []}, 'This release uses manual import; unsupported URL or stale catalog entry found')
    docs = {}
    for leaf in ('README.txt', 'NOTICES.txt'):
        record = manifest['playerDocs'][leaf]
        require(record['file'] == 'docs/player/' + leaf, 'Wrong player documentation path')
        contents = safe_relative(root, record['file']).read_bytes()
        require(digest(contents) == record['sha256'], 'Player documentation hash mismatch: ' + leaf)
        # Match a drive-letter token, not the final "s:/" within "https://".
        require(not re.search(rb'(?<![A-Za-z0-9_])[A-Za-z]:[\\/]', contents),
                'Private local path in player documentation')
        docs[leaf] = contents
    members = {expected_name: package, **docs,
               'SHA256SUMS.txt': (digest(package) + '  ' + expected_name + '\n').encode()}
    if archive_input:
        verify_zip(artifact,members)
    return manifest, members


def write_zip(path, members):
    require(not path.exists(), 'Refusing to overwrite ' + str(path))
    path.parent.mkdir(parents=True, exist_ok=True)
    with zipfile.ZipFile(path, 'x', compression=zipfile.ZIP_DEFLATED, compresslevel=9) as archive:
        for name, data in sorted(members.items()):
            entry = zipfile.ZipInfo(name, (2026, 10, 29, 0, 0, 0))
            entry.compress_type = zipfile.ZIP_DEFLATED
            entry.external_attr = 0o100644 << 16
            archive.writestr(entry, data, compresslevel=9)
    verify_zip(path, members)


def verify_zip(path, members):
    with zipfile.ZipFile(path) as archive:
        require(sorted(archive.namelist()) == sorted(members), 'Unexpected or duplicated ZIP contents')
        require(archive.testzip() is None, 'ZIP CRC failed')
        require(all(archive.read(name) == value for name, value in members.items()), 'ZIP payload mismatch')


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--root', type=Path, default=ROOT, help='Repository root (defaults beside tools/)')
    parser.add_argument('--artifact', type=Path, required=True, help='Previously downloaded release ZIP or JTMod; no automatic download')
    parser.add_argument('--out', type=Path, help='New ZIP path; default dist/ release filename')
    parser.add_argument('--verify-only', action='store_true')
    args = parser.parse_args()
    manifest, members = verified_inputs(args.root,args.artifact)
    result = dict(status='VERIFIED_EXISTING_JTMOD', packageSha256=manifest['jtmod']['sha256'],
                  scope='Offline package/manifest integrity only; not a game or listening test')
    if not args.verify_only:
        out = args.out or args.root / 'dist/WW-Prince-Model-Sword-Voice-0.6.0.zip'
        require(out.suffix.lower() == '.zip', 'Output must be a ZIP file')
        write_zip(out, members)
        result.update(zip=str(out), zipSha256=digest(out.read_bytes()), zipMembers=sorted(members))
    print(json.dumps(result, indent=2))


if __name__ == '__main__':
    main()
