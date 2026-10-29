# Installation and recovery

Download only the universal 0.5.0 JTMod. Apply it with PoP Mod Manager 2.1.2+, then close the manager and game and run `WWPrince-Model-Sword-Voice/Finish-Setup.cmd` in the game folder. Select the correct edition. Steam requires Large assets enabled first and the verified `POP3.EXE.popmm.bak` retained.

## Old installations and other mods

Restore/remove older separate model/sword packages before applying the universal one. Do not stack editions. Existing approved voice data is recognized without regeneration, provided its verified backup/receipt remains intact. Unknown sound banks, modified executables, other model stacks and different languages are refused, not overwritten.

OpenJade setup converts the manager-applied common model archive into the exact full-effects archive. Until the helper's Restore operation runs, Mod Manager may report the archive as externally changed. **Restore with the helper before changing or removing the Mod Manager selection.** Do not force reapply over modified data.

## Check and restore

`Manage-Mod.cmd` offers Install, Check and Restore. It defaults to its parent game folder. Advanced usage can pass `-Action Check -Edition Steam -GameDirectory "X:\Games\The Two Thrones"` directly to `Manage-Mod.ps1`.

Check verifies model/sword, voice and the required Steam executable state. A successful file check is not proof of all in-game dialogue playback. Restore reverses the helper changes first. Then use Mod Manager's Restore original, and disable Large assets on Steam.

Backups retained outside the added setup folder:

- Voice: `Sound/WW-Prince-Voice-Backups/`, with the installer's receipt.
- Steam interpreter: `WWPrinceWaterSwordBackup/POP3.EXE.before-interpreter-patch`.
- OpenJade effects: `WWPrinceEffectsBackup/pop3.bf.before-openjade-effects`.

Never delete backups while the mod is installed. No saves or unrelated files are intentionally removed.

## Failure handling

Helpers are individually guarded, **not one multi-file transaction**. If a later stage fails, an earlier component may already be installed or restored. Read the error, keep all backups, correct the stated issue and rerun. Known original/installed states are repeatable. Do not bypass hashes or replace backups with arbitrary files.

If files are missing or changed, restore helper changes first where possible, then remove/reapply the same JTMod with Mod Manager. If an unexpected modified archive or damaged backup prevents that, retain everything and investigate; do not force an overwrite. Setup needs approximately 2 GB of free temporary/backup space in addition to Mod Manager's needs.
