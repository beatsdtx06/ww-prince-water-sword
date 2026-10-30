# Installation and recovery

Import the JTMod under **OpenJade → The Two Thrones**, disable older WW Prince
packages, enable this one, Apply, launch. Do not use Classic/Steam.

## Upgrading from 0.5.x

Disable the older package first. Never enable both.

If you ran the old 0.5.0 **Finish Setup** helper, its changes are outside Mod
Manager's tracking. Undo them with that release's recovery steps, or start from
a verified original install. Do not force Apply past an external-change warning.

## WW voice still plays after uninstall

Cause: the private "WW Prince Voice - Development Preview 1" helper patched
`Sound/soundlocal.big` directly, so Mod Manager cannot undo it.

Fix, before installing 0.6.0:

1. Close the game and Mod Manager.
2. Check that `Sound/ww-prince-voice-install.json` names `WW Prince Voice - Development Preview 1`.
3. Check that `Sound/WW-Prince-Voice-Backups/soundlocal.7e810ba92128a00d505d1a89cb84adb97553cdc6bf5a8e4e4cf99b5487f9a627.big`
   exists and its SHA-256 is `7e810ba92128a00d505d1a89cb84adb97553cdc6bf5a8e4e4cf99b5487f9a627`.
4. Replace `Sound/soundlocal.big` with that backup.
5. Check that the new `Sound/soundlocal.big` has the same hash, then delete `Sound/ww-prince-voice-install.json` only.
6. Keep the backup folder.

After that, 0.6.0 installs and uninstalls cleanly through Mod Manager.

## Conflicts and errors

Other mods that edit `pop3.bf` or English `001.sb0` / `004.sb0` conflict with
this one. Test with this mod alone. On an unknown-bank or externally-modified
archive error, stop and keep your files and backups; do not bypass the check.
