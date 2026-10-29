# Verification scope

The universal JTMod uses the accepted Steam 0.4.0 BF edits unchanged. OpenJade Finish Setup reconstructs the accepted OpenJade 0.4.0 full-effects BF byte-for-byte. The approved 93 voice payloads and final sound-bank hash are unchanged. Historical component evidence is retained in `model-verification-0.4.0.json`.

Automated checks cover JTMod integrity, one catalog entry, safe embedded paths, every embedded file hash, all 93 payloads, exclusion of held clips, absence of full game archives/executables/weights and private paths in current runtime text, and deterministic rebuilding.

Real-archive-copy integration checks cover both editions: extracted setup install/check/repeat/restore; exact expected BF/voice/executable results; unchanged FAT; unchanged voice bytes outside the 93 patch ranges; wrong model rejection; corrupted setup payload rejection. The new OpenJade delta is output-hash-checked before replacing the archive and retains a verified baseline backup. Standalone voice-installer safety tests cover 12 synthetic failure/restore cases.

Mod Manager 2.1.2 accepted the v9 added-file format in a private import probe. Final import/application evidence and actual automated run results are recorded separately in `release-verification.json` at the repository root, not recursively embedded in the artifact it describes.

These are archive/installer checks, not a new full campaign. All 93 lines and every save state have not been played through. A copied Steam installation's launcher refused to start outside its normal installation location; no unsupported full-OpenJade-on-Steam behavior is shipped. Instead, the exact previously accepted edition-specific archive states are retained. Unknown revisions, languages, overlapping mods and other OpenJade versions are not claimed compatible.

The release test suite changes disposable copies only. Existing installed game archives, mod selections and saves are not altered.
