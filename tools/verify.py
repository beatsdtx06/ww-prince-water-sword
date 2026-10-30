"""Verify a downloaded 0.6.0 release JTMod offline, or run synthetic self-tests.

Standard library only. Reads files; never downloads, writes or patches anything.
"""
import argparse
from copy import deepcopy
import hashlib
import json
from pathlib import Path
import re
import tempfile
import unittest

from jtmod import blob, model_fingerprint, read_v9, require, seal, u32, unseal

ROOT = Path(__file__).resolve().parents[1]
JTMOD = 'WW-Prince-Model-Sword-Voice-0.6.0.jtmod'
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


def verify(root, artifact):
    manifest = read_json(root / 'package-manifest.json')
    require(manifest.get('version') == '0.6.0' and manifest.get('target') == 'openjade'
            and manifest.get('jtmodVersion') == 9, 'This tool handles the OpenJade 0.6.0 release only')
    require(manifest.get('coverageCounts') == COUNTS, 'Unexpected coverage declaration')
    require(manifest.get('intentionalExclusions') == EXCLUSIONS, 'Missing intentional exclusions')
    require(manifest.get('scriptsRequired') is False and manifest.get('executableFiles') == 0,
            'Helpers/executables are not part of this release')
    require(manifest.get('modelBins') == 61, 'Unexpected model operation count')
    jtmod = manifest['jtmod']
    require(jtmod['file'] == JTMOD and jtmod.get('downloadUrl') == RELEASE_URL + JTMOD,
            'Unexpected JTMod release-asset identity')
    require(artifact is not None, 'Pass --artifact with the downloaded release JTMod')
    artifact = Path(artifact)
    require(artifact.is_file(), 'Downloaded artifact does not exist: ' + str(artifact))
    require(artifact.suffix.lower() == '.jtmod', 'Artifact must be the release JTMod')
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
    require(read_json(root / 'pmm_manifest.json') == {'mods': []},
            'This release uses manual import; unsupported URL or stale catalog entry found')
    return manifest


def fixture_package():
    """Symbolic bytes only: no real game or audio assets."""
    payloads = [b'model', b'stream', b'dialogue-bank', b'effort-bank']
    core = b'JADEJTM1' + u32(9) + u32(0) + blob('T2T') + blob('pop3.bf') + bytes(40)
    core += b''.join(blob(v) for v in ['Unit-test fixture', 'beatsdtx06', '0.6.0',
                                      'Not a usable game mod', '2026-10-29', 'test'])
    core += blob(b'') + u32(0) + u32(len(payloads))
    for payload in payloads:
        core += b'\0' + u32(len(payload)) + u32(len(payload)) + payload
    core += u32(61) + b''.join(u32(index) + b'\2' + u32(0) for index in range(61))
    core += u32(3)
    for i, (mode, path, original) in enumerate(OPERATIONS, 1):
        core += bytes([mode]) + blob(path) + blob('soundlocal') + blob('') + blob(original) + u32(i)
    return seal(core)


def fixture_root(root):
    data = fixture_package()
    decoded = read_v9(data)
    (root / JTMOD).write_bytes(data)
    manifest = dict(version='0.6.0', target='openjade', jtmodVersion=9,
                    scriptsRequired=False, executableFiles=0, modelBins=61,
                    modelPayloadSha256=model_fingerprint(decoded),
                    coverageCounts=COUNTS, intentionalExclusions=EXCLUSIONS,
                    operations=[dict(op, bytes=len(decoded['files'][op['path']]),
                                     sha256=digest(decoded['files'][op['path']]))
                                for op in decoded['operations']],
                    jtmod=dict(file=JTMOD, bytes=len(data), sha256=digest(data),
                               downloadUrl=RELEASE_URL + JTMOD))
    for name, value in [('package-manifest.json', manifest), ('pmm_manifest.json', dict(mods=[]))]:
        (root / name).write_text(json.dumps(value), encoding='utf-8')
    return manifest


class IntegrityTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory(prefix='ww-prince-public-test-')
        self.root = Path(self.temp.name)
        self.manifest = fixture_root(self.root)

    def tearDown(self):
        self.temp.cleanup()

    def write_manifest(self, value):
        (self.root / 'package-manifest.json').write_text(json.dumps(value), encoding='utf-8')

    def verify(self):
        return verify(self.root, self.root / JTMOD)

    def assert_rejected(self, edit):
        wrong = deepcopy(self.manifest)
        edit(wrong)
        self.write_manifest(wrong)
        with self.assertRaises(ValueError):
            self.verify()

    def test_valid_synthetic_package(self):
        self.assertEqual(self.verify()['coverageCounts'], COUNTS)

    def test_native_payload_manifest_tampering_rejected(self):
        self.assert_rejected(lambda m: m['operations'][1].update(sha256='0' * 64))

    def test_model_fingerprint_tampering_rejected(self):
        self.assert_rejected(lambda m: m.update(modelPayloadSha256='0' * 64))

    def test_stale_release_rejected(self):
        self.assert_rejected(lambda m: m.update(version='0.5.1'))

    def test_incorrect_counts_rejected(self):
        self.assert_rejected(lambda m: m['coverageCounts'].update(isolatedDialogueClips=93))

    def test_tampered_artifact_rejected(self):
        (self.root / JTMOD).write_bytes(fixture_package()[:-1] + b'x')
        with self.assertRaises(ValueError):
            self.verify()

    def test_unsealed_package_rejected(self):
        with self.assertRaises(ValueError):
            read_v9(fixture_package()[:-1] + b'x')

    def test_truncated_resealed_package_rejected(self):
        with self.assertRaises(ValueError):
            read_v9(seal(unseal(fixture_package())[:-4]))

    def test_stale_or_url_catalog_entry_rejected(self):
        pmm = dict(mods=[dict(file=RELEASE_URL + JTMOD, sha256='0' * 64)])
        (self.root / 'pmm_manifest.json').write_text(json.dumps(pmm), encoding='utf-8')
        with self.assertRaises(ValueError):
            self.verify()

    def test_missing_artifact_rejected(self):
        with self.assertRaises(ValueError):
            verify(self.root, None)


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--root', type=Path, default=ROOT)
    parser.add_argument('--self-test', action='store_true')
    parser.add_argument('--artifact', type=Path, help='Downloaded release JTMod; required except with --self-test')
    args = parser.parse_args()
    if args.self_test:
        result = unittest.TextTestRunner(verbosity=2).run(unittest.defaultTestLoader.loadTestsFromTestCase(IntegrityTests))
        raise SystemExit(0 if result.wasSuccessful() else 1)
    if args.artifact is None:
        parser.error('--artifact is required; the JTMod is a release asset, not a Git file')
    manifest = verify(args.root, args.artifact)
    print(json.dumps(dict(status='OFFLINE_PACKAGE_CHECKS_PASSED', packageSha256=manifest['jtmod']['sha256'],
                          nativePayloads=len(manifest['operations']), runtimeTest=False), indent=2))


if __name__ == '__main__':
    main()
