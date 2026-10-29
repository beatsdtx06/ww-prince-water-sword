"""Check the current public package, or run small synthetic integrity regressions."""
import argparse
from copy import deepcopy
import json
from pathlib import Path
import tempfile
import unittest

import package_release as package
from jtmod import blob, model_fingerprint, read_v9, seal, u32, unseal


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
    for i, (mode, path, original) in enumerate(package.OPERATIONS, 1):
        core += bytes([mode]) + blob(path) + blob('soundlocal') + blob('') + blob(original) + u32(i)
    return seal(core)


def fixture_root(root):
    data = fixture_package()
    decoded = read_v9(data)
    filename = 'WW-Prince-Model-Sword-Voice-0.6.0.jtmod'
    (root / filename).write_bytes(data)
    (root / 'docs/player').mkdir(parents=True)
    docs = {}
    for name in ['README.txt', 'NOTICES.txt']:
        raw = ('Synthetic test-only ' + name + '\n').encode()
        path = 'docs/player/' + name
        (root / path).write_bytes(raw)
        docs[name] = dict(file=path, sha256=package.digest(raw))
    manifest = dict(version='0.6.0', target='openjade', jtmodVersion=9,
                    scriptsRequired=False, executableFiles=0, modelBins=61,
                    modelPayloadSha256=model_fingerprint(decoded),
                    coverageCounts=package.COUNTS, intentionalExclusions=package.EXCLUSIONS,
                    playerDocs=docs,
                    operations=[dict(op, bytes=len(decoded['files'][op['path']]),
                                     sha256=package.digest(decoded['files'][op['path']]))
                                for op in decoded['operations']],
                    jtmod=dict(file=filename, bytes=len(data), sha256=package.digest(data),
                               downloadUrl=package.RELEASE_URL+filename))
    pmm = dict(mods=[])
    zipname = 'WW-Prince-Model-Sword-Voice-0.6.0.zip'
    members = {filename:data,**{name:(root/record['file']).read_bytes() for name,record in docs.items()},
               'SHA256SUMS.txt':(package.digest(data)+'  '+filename+'\n').encode()}
    package.write_zip(root/zipname,members)
    manifest['zip'] = dict(file=zipname,bytes=(root/zipname).stat().st_size,
                          sha256=package.digest((root/zipname).read_bytes()),downloadUrl=package.RELEASE_URL+zipname)
    for name, value in [('package-manifest.json', manifest), ('pmm_manifest.json', pmm)]:
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
        return package.verified_inputs(self.root,self.root/self.manifest['jtmod']['file'])

    def test_valid_synthetic_package(self):
        manifest, members = self.verify()
        self.assertEqual(manifest['coverageCounts'], package.COUNTS)
        self.assertEqual(len(members), 4)

    def test_native_payload_manifest_tampering_rejected(self):
        wrong = deepcopy(self.manifest)
        wrong['operations'][1]['sha256'] = '0' * 64
        self.write_manifest(wrong)
        with self.assertRaises(ValueError):
            self.verify()

    def test_model_fingerprint_tampering_rejected(self):
        wrong = deepcopy(self.manifest)
        wrong['modelPayloadSha256'] = '0' * 64
        self.write_manifest(wrong)
        with self.assertRaises(ValueError):
            self.verify()

    def test_stale_release_rejected(self):
        wrong = deepcopy(self.manifest)
        wrong['version'] = '0.5.1'
        self.write_manifest(wrong)
        with self.assertRaises(ValueError):
            self.verify()

    def test_incorrect_counts_rejected(self):
        wrong = deepcopy(self.manifest)
        wrong['coverageCounts']['isolatedDialogueClips'] = 93
        self.write_manifest(wrong)
        with self.assertRaises(ValueError):
            self.verify()

    def test_duplicate_and_unexpected_zip_members_rejected(self):
        import zipfile
        _, members = self.verify()
        target = self.root / 'bad.zip'
        with zipfile.ZipFile(target, 'w') as archive:
            for name, value in members.items():
                archive.writestr(name, value)
            archive.writestr('extra.wav', b'not allowed')
        with self.assertRaises(ValueError):
            package.verify_zip(target, members)

    def test_zip_deterministic_and_nonoverwriting(self):
        _, members = self.verify()
        first, second = self.root / 'a.zip', self.root / 'b.zip'
        package.write_zip(first, members)
        package.write_zip(second, members)
        self.assertEqual(first.read_bytes(), second.read_bytes())
        with self.assertRaises(ValueError):
            package.write_zip(first, members)

    def test_documentation_hash_required(self):
        (self.root / 'docs/player/README.txt').write_text('tamper', encoding='utf-8')
        with self.assertRaises(ValueError):
            self.verify()

    def test_https_documentation_is_not_a_windows_drive(self):
        raw = b'https://github.com/beatsdtx06/ww-prince-water-sword\n'
        (self.root/'docs/player/README.txt').write_bytes(raw)
        self.manifest['playerDocs']['README.txt']['sha256'] = package.digest(raw)
        self.write_manifest(self.manifest)
        self.verify()

    def test_hash_bound_private_windows_path_is_still_rejected(self):
        raw = b'Private path: C:/Users/test/local.wav\n'
        (self.root/'docs/player/README.txt').write_bytes(raw)
        self.manifest['playerDocs']['README.txt']['sha256'] = package.digest(raw)
        self.write_manifest(self.manifest)
        with self.assertRaisesRegex(ValueError,'Private local path'):
            self.verify()

    def test_unsealed_package_rejected(self):
        with self.assertRaises(ValueError):
            read_v9(fixture_package()[:-1] + b'x')

    def test_truncated_resealed_package_rejected(self):
        with self.assertRaises(ValueError):
            read_v9(seal(unseal(fixture_package())[:-4]))

    def test_traversal_rejected(self):
        with self.assertRaises(ValueError):
            package.safe_relative(self.root, '../outside.txt')
        with self.assertRaises(ValueError):
            package.safe_relative(self.root, 'C:/outside.txt')

    def test_stale_or_url_catalog_entry_rejected(self):
        path = self.root / 'pmm_manifest.json'
        pmm = json.loads(path.read_text())
        pmm['mods'] = [dict(file=package.RELEASE_URL+self.manifest['jtmod']['file'],sha256='0'*64)]
        path.write_text(json.dumps(pmm), encoding='utf-8')
        with self.assertRaises(ValueError):
            self.verify()

    def test_downloaded_zip_is_verified_without_extraction(self):
        manifest,members = package.verified_inputs(self.root,self.root/self.manifest['zip']['file'])
        self.assertEqual(len(members),4)
        self.assertEqual(manifest['version'],'0.6.0')

    def test_missing_external_artifact_rejected(self):
        with self.assertRaises(ValueError):
            package.verified_inputs(self.root,None)


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--root', type=Path, default=package.ROOT)
    parser.add_argument('--self-test', action='store_true')
    parser.add_argument('--artifact', type=Path, help='Downloaded release ZIP or JTMod; required except with --self-test')
    parser.add_argument('--zip', type=Path, help='Also compare a ZIP with the verified package and docs')
    args = parser.parse_args()
    if args.self_test:
        result = unittest.TextTestRunner(verbosity=2).run(unittest.defaultTestLoader.loadTestsFromTestCase(IntegrityTests))
        raise SystemExit(0 if result.wasSuccessful() else 1)
    if args.artifact is None:
        parser.error('--artifact is required for release verification; binaries are release assets, not Git files')
    manifest, members = package.verified_inputs(args.root,args.artifact)
    if args.zip:
        package.verify_zip(args.zip, members)
    print(json.dumps(dict(status='OFFLINE_PUBLIC_PACKAGE_CHECKS_PASSED',
                          packageSha256=manifest['jtmod']['sha256'],
                          nativePayloads=len(manifest['operations']),
                          runtimeTest=False, fullCampaignRuntimeVerified=False), indent=2))


if __name__ == '__main__':
    main()
