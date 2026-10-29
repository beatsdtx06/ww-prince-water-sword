"""Exercise installer against disposable local fixtures, never installed games."""
import hashlib
import json
from pathlib import Path
import shutil
import subprocess
import tempfile
import unittest

ROOT=Path(__file__).resolve().parents[1]
SHELL=shutil.which('powershell.exe') or shutil.which('pwsh.exe')


def sha(data):
    return hashlib.sha256(data).hexdigest()


class InstallerTests(unittest.TestCase):
    def setUp(self):
        self.temporary=tempfile.TemporaryDirectory(prefix='ww-voice-test-')
        self.addCleanup(self.temporary.cleanup)
        self.root=Path(self.temporary.name)
        self.package=self.root/'package'
        self.game=self.root/'game'
        (self.game/'Sound').mkdir(parents=True)
        (self.package/'patches').mkdir(parents=True)
        shutil.copy2(ROOT/'voice/Manage-Voice.ps1',self.package/'Manage-Voice.ps1')
        self.original=bytes(range(256))*4
        self.fat=b'test-fat-do-not-change'
        self.payload=b'changed!'
        altered=bytearray(self.original)
        altered[200:208]=self.payload
        self.changed=bytes(altered)
        self.archive=self.game/'Sound/soundlocal.big'
        self.archive.write_bytes(self.original)
        (self.game/'Sound/soundlocal.fat').write_bytes(self.fat)
        (self.package/'patches/270.bin').write_bytes(self.payload)
        self.manifest=dict(formatVersion=1,package='test-fixture',archiveBytes=len(self.original),
            baseSha256=sha(self.original),patchedSha256=sha(self.changed),fatSha256=sha(self.fat),
            patches=[dict(index=270,start=200,length=8,file='patches/270.bin',
                          sha256=sha(self.payload),originalSha256=sha(self.original[200:208]))])
        self.save_manifest()

    def save_manifest(self):
        (self.package/'manifest.json').write_text(json.dumps(self.manifest))

    def run_action(self,action,success=True,error_contains=None):
        run=subprocess.run([SHELL,'-NoProfile','-ExecutionPolicy','Bypass','-File',
            str(self.package/'Manage-Voice.ps1'),'-Action',action,'-GamePath',str(self.game)],
            capture_output=True,text=True)
        self.assertEqual(run.returncode==0,success,run.stdout+'\n'+run.stderr)
        if not success:
            self.assertIsNotNone(error_contains,'Negative tests must check the actual rejection reason')
            self.assertIn(error_contains,run.stdout+'\n'+run.stderr)
        self.assertEqual((self.game/'Sound/soundlocal.fat').read_bytes(),self.fat)
        return run

    def test_check_readonly(self):
        self.run_action('Check')
        self.assertEqual(self.archive.read_bytes(),self.original)
        self.assertFalse((self.game/'Sound/WW-Prince-Voice-Backups').exists())

    def test_install_uninstall_idempotent(self):
        self.run_action('Install')
        self.assertEqual(self.archive.read_bytes(),self.changed)
        backup=self.game/f'Sound/WW-Prince-Voice-Backups/soundlocal.{sha(self.original)}.big'
        self.assertEqual(backup.read_bytes(),self.original)
        self.run_action('Install')
        self.run_action('Uninstall')
        self.assertEqual(self.archive.read_bytes(),self.original)
        self.assertEqual(backup.read_bytes(),self.original)
        self.assertFalse((self.game/'Sound/ww-prince-voice-install.json').exists())
        self.run_action('Uninstall')

    def test_modified_archive_refused(self):
        modified=b'X'+self.original[1:]
        self.archive.write_bytes(modified)
        self.run_action('Install',False,'Archive differs from both supported states')
        self.assertEqual(self.archive.read_bytes(),modified)

    def test_modified_installed_archive_not_overwritten(self):
        self.run_action('Install')
        modified=b'X'+self.changed[1:]
        self.archive.write_bytes(modified)
        self.run_action('Uninstall',False,'Archive differs from both supported states')
        self.assertEqual(self.archive.read_bytes(),modified)

    def test_corrupt_payload_refused(self):
        (self.package/'patches/270.bin').write_bytes(b'corrupt!')
        self.run_action('Install',False,'Patch checksum mismatch')
        self.assertEqual(self.archive.read_bytes(),self.original)

    def test_unsafe_path_refused(self):
        self.manifest['patches'][0]['file']='../outside.bin'
        self.save_manifest()
        self.run_action('Install',False,'Unsafe patch filename')
        self.assertEqual(self.archive.read_bytes(),self.original)

    def test_overlap_refused(self):
        self.manifest['patches'].append(self.manifest['patches'][0].copy())
        self.save_manifest()
        self.run_action('Install',False,'Invalid or overlapping patch range')
        self.assertEqual(self.archive.read_bytes(),self.original)

    def test_out_of_bounds_refused(self):
        self.manifest['patches'][0]['start']=1020
        self.save_manifest()
        self.run_action('Install',False,'Invalid or overlapping patch range')
        self.assertEqual(self.archive.read_bytes(),self.original)

    def test_wrong_fat_refused(self):
        self.manifest['fatSha256']='0'*64
        self.save_manifest()
        self.run_action('Install',False,'Unsupported sound FAT')
        self.assertEqual(self.archive.read_bytes(),self.original)

    def test_corrupt_backup_refused(self):
        backup=self.game/f'Sound/WW-Prince-Voice-Backups/soundlocal.{sha(self.original)}.big'
        backup.parent.mkdir()
        backup.write_bytes(b'not original')
        self.run_action('Install',False,'Backup verification failed')
        self.assertEqual(self.archive.read_bytes(),self.original)
        self.assertEqual(backup.read_bytes(),b'not original')

    def test_missing_backup_refuses_restore(self):
        self.archive.write_bytes(self.changed)
        self.run_action('Uninstall',False,'Original backup is missing')
        self.assertEqual(self.archive.read_bytes(),self.changed)

    def test_conflicting_receipt_refused(self):
        receipt=self.game/'Sound/ww-prince-voice-install.json'
        receipt.write_text('{"patchedSha256":"different"}')
        self.run_action('Install',False,'existing installation receipt')
        self.assertEqual(self.archive.read_bytes(),self.original)


if __name__=='__main__':
    unittest.main(verbosity=2)
