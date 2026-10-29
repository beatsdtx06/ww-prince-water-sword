# Warrior Within Prince — Model, Water Sword & Voice

**0.6.0 · OpenJade only · by beatsdtx06**

One mod containing the Warrior Within Prince model, Water Sword from New Game,
enhanced damage and boss-only blue aura, plus expanded English Prince dialogue
and original WW gameplay effort sounds. The conversion follows The Two Thrones
dialogue and preserves slot timing; it is not a new performance recorded by the actor.

[Download the ZIP](https://github.com/beatsdtx06/ww-prince-water-sword/releases/download/v0.6.0/WW-Prince-Model-Sword-Voice-0.6.0.zip)

The ZIP and optional raw JTMod are GitHub release assets. Git contains the
documentation, hashes, catalog and verification/repackaging tools, not the large
binary mod itself. The ZIP still contains exactly one JTMod.
This version is installed by manual import of that downloaded file. Its
repository catalog is intentionally empty: Mod Manager's catalog requires a
repository-relative JTMod path and cannot point at these release-asset URLs.

## Install

Requires an existing OpenJade 0.5.1 TTT installation with supported English audio
and PoP Mod Manager 2.1.2 with native JTMod v9 support. These are the tested
versions, not a compatibility claim for every future engine/manager release.

1. Download and extract the ZIP.
2. Import `WW-Prince-Model-Sword-Voice-0.6.0.jtmod` into Mod Manager for **OpenJade → The Two Thrones**.
3. Disable older WW Prince/model/sword/voice editions, enable this one, and Apply.
4. Launch the game.

No CMD, PowerShell, Finish Setup helper, executable patch, API key or AI runtime
is required. Do not install this package under Classic/Steam. Back up saves and
retain Mod Manager's backups. [Installation and recovery](docs/INSTALLATION.md).

## Contents and voice coverage

The ZIP contains exactly one `.jtmod`, `README.txt`, `NOTICES.txt`, and
`SHA256SUMS.txt`. The JTMod contains:

- 61 native `pop3.bf` model/script record edits preserving the accepted OpenJade model, sword and effects.
- `sound/english/wwprince.ls0`: the voice payload stream.
- `sound/english/001.sb0`: guarded English dialogue-bank replacement directing the selected records to that stream.
- `sound/english/004.sb0`: guarded resident bank replacement containing the native WW effort sounds.

Audio is installed inside the sound archives by Mod Manager. No whole game
archive, game executable, DLL, source WAV collection or voice model is shipped.
[Exact payload hashes](package-manifest.json).

Voice coverage is **110 isolated spoken clips, 80 mapped Prince turns across 38
in-engine scene tracks, and 28 native WW vocal resources**: 26 resident gameplay
efforts plus two mapped death/fall sounds. Mixed scenes retain
other characters and samples outside the Prince's mapped turns. Pre-rendered
videos, the Dark Prince and other speakers remain original. Additional nonverbal
resources without reliable action/speaker mapping are intentionally excluded; this is not a claim that every
possible vocalization in the game has been replaced.
[Detailed coverage and limitations](docs/VOICE-COVERAGE.md).
This release retains documented narrow wording uncertainties, including the
interrupted scene 49 endpoint and the provenance-verified scene 55 phrase;
it does not claim perfect ASR agreement or a full-campaign listening review.
[Release notes and known limits](docs/RELEASE-NOTES.md).

## Verification and restoration

The release has file-level, decoding and scoped gameplay evidence; it has not
received a complete campaign playthrough. A decoder check is not listening
approval, and historical opening tests are not full-release campaign tests.
[Exact test boundaries](docs/TESTS.md).

Close the game and choose Mod Manager's **Restore original** to uninstall.
Keep its backups. Do not stack overlapping model or English-audio mods.
[Compatibility](docs/COMPATIBILITY.md) · [Public packaging](BUILD.md).

Unofficial fan mod, with no Ubisoft or voice-actor endorsement. [Notices](NOTICES.md).
