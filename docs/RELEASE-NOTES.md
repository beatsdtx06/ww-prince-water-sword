# 0.6.0 — WW Prince, Water Sword and expanded voice

One native JTMod for OpenJade The Two Thrones. Download the release ZIP, extract
it, import the JTMod in Mod Manager, disable older overlapping editions, Apply,
then launch. No Finish Setup script, API key or AI runtime is required. Steam /
the original Classic engine is not a supported target of this release.

## Included

- The accepted WW Prince model, Water Sword from New Game, enhanced damage and boss-only blue aura.
- 110 isolated spoken clips and 80 mapped Prince turns across 38 in-engine scene tracks.
- 26 native WW gameplay effort resources and two mapped native death/fall sounds.
- Complete PCM headers and native archive operations, with original-bank guards.

The ZIP contains exactly one JTMod, README.txt, NOTICES.txt and SHA256SUMS.txt.
The optional raw JTMod download is the same mod. Both binaries are release
assets; the repository contains documentation, hashes and offline verification /
repackaging tools. Its automatic Mod Manager catalog is intentionally empty
because this manager requires repository-relative JTMod paths.

## Known limits

- One very short interrupted final of in the Babylon reminiscence has uncertain articulation; automatic recognition omits it. This is not a verbatim-perfect or full-campaign listening certification.
- The what-of repair uses an accepted same-voice phrase with a short coarticulated entry crossfade. Recognition differs by model; exact provenance and reconstruction were checked.
- Eight additional known-normal-Prince nonverbal resources lack reliable action-specific replacement mapping; 13 further nonverbal resources remain unclassified. They are intentionally left original.
- Pre-rendered video audio, the Dark Prince and other speakers remain original. Only the supported English audio layout on OpenJade is targeted.
- No complete campaign playthrough or final-package subjective listening certification is claimed. The final four hurt-slot corrections and two death/fall mappings have offline provenance/format checks, not individual in-game trigger confirmation.

Mixed scenes preserve other speakers and samples outside mapped Prince turns.
Pre-rendered videos, the Dark Prince, other characters and unresolved extra
nonverbal resources remain original. These counts are not a claim of replacing
every possible vocalization or completing a full campaign playthrough.

Word repairs retain original generation and failed-ASR evidence. Where source
and converted recognition disagree, explicit donor provenance and deterministic
sample reconstruction are distinguished from an automated wording pass; neither
is falsely described as subjective listening approval.

## Verification scope

Static and offline: 48 safety regression tests passed. Final native JTMod integrity, 61 accepted model/script records, original-bank guards, unchanged historical base stream bytes and later approved PCM homecoming were verified. All 55 newly added primary-bank records and 26 resident effort resources passed complete decoding/PCM checks; scene durations and protected other-speaker samples were checked. Word-repair provenance and reconstruction were independently verified; the two documented wording/articulation qualifications remain.

Installation and restoration: Final package native sound operations passed independent archive apply, byte-exact restoration and deterministic reapply against verified originals, preserving 34 unrelated archive entries. The same append-only algorithm had previously matched actual Mod Manager baseline output byte for byte. The final applied sound pair was placed directly in a separately backed-up disposable OpenJade copy and hash-verified; this is not a new final-package Mod Manager UI Apply/Restore test. No main game or main save was modified.

Runtime and listening: On 2026-10-29, the final hash-bound package reached the OpenJade 0.5.1 Vulkan menu and live gameplay from a disposable Palace Balcony save. The WW Prince and Water Sword were visibly present; sampled frame overlays were 59.9-60.0 FPS. The homecoming subtitle sequence appeared. A jump input was sent, but no frame-by-frame animation/audio synchronization or audible output was independently certified. Menu navigation did not reliably select New Game, so this final run is an existing-save smoke test, not a fresh New Game test. Earlier user tests confirmed New Game/Water Sword, corrected opening dialogue/music/effects, and native WW efforts in their earlier packages. The final run exited via normal window close. Its log contains a pre-profile-activation save warning followed by successful activation of the disposable profile; no audio decoding or crash error was logged. Sampled FPS is not a comprehensive performance benchmark.

See [coverage](VOICE-COVERAGE.md), [test boundaries](TESTS.md), and
[installation / recovery](INSTALLATION.md). Keep Mod Manager's backups and use
Restore original to uninstall. This is an unofficial fan mod with no Ubisoft
or voice-actor endorsement.
