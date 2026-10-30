# Installation, upgrading and recovery

Extract the 0.6.0 ZIP, import its one JTMod under **OpenJade → The Two Thrones**,
disable older WW Prince/model/sword/voice packages, enable this one, Apply, and
launch. No helper script or extra setup is used. Do not select Classic/Steam.

## Upgrading from 0.5.0 or 0.5.1

If you only imported/applied the old JTMod and never ran the 0.5.0 Finish Setup
helper, disable the older package before applying this one. Never enable both.

If you previously ran an old helper, some changes may be outside the manager's
tracking. Preserve existing backups and receipts. Recover those helper-owned
changes using the old release's documented recovery procedure, or recover a
verified original installation separately. Do not force Apply over an unexpected
external-change warning or bypass original hash guards. Old-helper recovery is
not a normal installation requirement of 0.6.0.

## Development Preview 1 leftover voice

Symptom: Mod Manager Restore / disable / delete returns the original Prince model
and Water Sword, but WW dialogue still plays.

Cause: the earlier private "WW Prince Voice - Development Preview 1" helper
patched `Sound/soundlocal.big` directly. That patch is not owned by the 0.6.0
JTMod, so Mod Manager cannot undo it when you remove this package.

Recovery before installing 0.6.0:

1. Close the game and Mod Manager.
2. Confirm `Sound/ww-prince-voice-install.json` names package
   `WW Prince Voice - Development Preview 1`.
3. Confirm `Sound/WW-Prince-Voice-Backups/soundlocal.7e810ba92128a00d505d1a89cb84adb97553cdc6bf5a8e4e4cf99b5487f9a627.big`
   exists and hashes to
   `7e810ba92128a00d505d1a89cb84adb97553cdc6bf5a8e4e4cf99b5487f9a627`.
4. Replace `Sound/soundlocal.big` with that backup (atomic replace preferred).
5. Verify the live archive hash is
   `7e810ba92128a00d505d1a89cb84adb97553cdc6bf5a8e4e4cf99b5487f9a627`, then
   delete `Sound/ww-prince-voice-install.json` only.
6. Keep the backup folder. Do not delete Steam/OpenJade backups blindly.

After that restore, Apply 0.6.0 on a clean English archive. Later uninstalls of
0.6.0 through Mod Manager Restore original then remove both model and voice.

## Other mods and uninstalling

Overlapping `pop3.bf` edits or English `001.sb0`/`004.sb0` replacements may conflict.
Use this combined mod by itself when checking a problem. Save files are not
replaced by this package; back them up before changing mods anyway.

Close the game and choose **Restore original** in Mod Manager to uninstall.
Retain the manager's backups. On an unknown-bank or externally-modified archive
error, stop and preserve the files/backups. Confirm the intended OpenJade game
folder and supported English audio; do not guess or bypass verification.
