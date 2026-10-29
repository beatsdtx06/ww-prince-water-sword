# Installation and recovery

For a supported OpenJade installation: extract the 0.5.1 ZIP, import its one JTMod, enable it, Apply, launch. No script or extra installer is used. Select **OpenJade → The Two Thrones**, not Classic.

## Upgrading from 0.5.0

If you only imported/applied the old JTMod and did **not** run Finish Setup, disable that old package and enable 0.5.1 before applying. Do not enable both. Mod Manager owns and removes the old package's added helper files when changing its selection.

If you previously **ran** an old helper, your game may contain changes outside Mod Manager's tracking. Preserve all existing backups and receipts. Restore those old helper-owned changes using the old release's documented recovery process before removing its files, or recover a verified original game installation separately. This is legacy recovery, not an installation requirement of 0.5.1. Do not force Apply over an externally modified archive.

The original reported installation used import/apply only; the new native package removes the previously mandatory helper step. A full diagnosis of every possible crash or unrelated mod conflict is not claimed.

## Other mods

Disable old WW Prince/model/sword/voice editions. Test this mod by itself first if the game crashes. Other model replacements and modifications to English `001.sb0` can conflict. Save backups and manager backups should be retained. No saves are replaced by this package.

## Uninstall

Close the game and choose **Restore original** in Mod Manager. There is no new helper to run. The native package's model and sound archive changes participate in the manager's normal restore operation.

On an unknown-bank error or unexpected external-change warning, stop and preserve the files/backups. Do not bypass hashes. Ensure the selected folder is the intended OpenJade game and the audio is the supported English version.
