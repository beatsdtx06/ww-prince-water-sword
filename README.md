# Warrior Within Prince — Model, Water Sword & Voice

**0.5.1 · OpenJade only · by beatsdtx06**

One mod: the Warrior Within Prince model, Water Sword from New Game, enhanced damage and boss-only blue aura, plus the approved **93-line English Prince voice preview**. The converted voice retains The Two Thrones dialogue and timing; it is not a new recording by the original actor.

**[Download the ZIP](https://github.com/beatsdtx06/ww-prince-water-sword/releases/download/v0.5.1/WW-Prince-Model-Sword-Voice-0.5.1.zip)**

## Install

Requires an existing **OpenJade 0.5.1** installation of The Two Thrones, the supported English game audio, and **PoP Mod Manager 2.1.2** with JTMod v9 support. Other engine revisions have not been verified. Back up saves and allow space for Mod Manager's backups.

1. Download and extract the ZIP.
2. Import **`WW-Prince-Model-Sword-Voice-0.5.1.jtmod`** into Mod Manager for **OpenJade → The Two Thrones**.
3. Disable older WW Prince/model/sword/voice packages, enable this one, and **Apply**.
4. Launch the game.

**No CMD, PowerShell, extra installer, executable patch, API key, or Finish Setup step.** All three components are installed directly by Mod Manager. Original Steam-engine support has been dropped; do not install this package under Classic/Steam.

If you only imported the old 0.5.0 JTMod and never ran its helper, disable it before applying 0.5.1. If you previously ran an old helper or Mod Manager reports externally modified files, retain your backups and follow [recovery guidance](docs/INSTALLATION.md) before changing the selection.

## Included files and behavior

The ZIP contains exactly one `.jtmod`, `README.txt`, `NOTICES.txt`, and `SHA256SUMS.txt`.

The JTMod contains:

- Native `pop3.bf` record edits for the WW Prince, hair, medallion, Water Sword, clean-start weapon grant, enhanced damage and boss-only blue aura. These preserve the accepted OpenJade 0.4.0 model/effects records.
- `sound/english/wwprince.ls0`: all **93 approved encoded voice clips**, unchanged.
- `sound/english/001.sb0`: an exact-original-hash-guarded replacement bank redirecting only those 93 records to the new stream. Other records and internal audio are preserved.

These audio entries are installed **inside the game's sound archives**, not as loose files requiring another setup step. No game executable or engine DLL is bundled. [Complete operation manifest](package-manifest.json).

Voice coverage is partial: 93 lines, about 7 minutes 53 seconds. The 17 held spoken candidates, 13 ambiguous/nonverbal records, mixed cinematics, Dark Prince, and other characters remain original. [Coverage details](docs/VOICE-COVERAGE.md).

## Restore and compatibility

Close the game and use Mod Manager's **Restore original**. Keep its backups. A native Apply → Restore → Apply cycle has been checked against exact original and modded archive hashes in a disposable game copy.

Do not stack this with older WW Prince editions or other mods replacing the same model or English voice bank. Compatibility with arbitrary mod stacks is not claimed. [Supported hashes](docs/COMPATIBILITY.md) · [Verification scope](docs/TESTS.md).

The obsolete 0.5.0 helper-based release remains in release history for recovery; it is not the recommended download. Developer source and historical reconstruction inputs are separate from the player ZIP. [Build instructions](BUILD.md).

Unofficial fan mod; no Ubisoft or voice-actor endorsement. See [notices](NOTICES.md).
