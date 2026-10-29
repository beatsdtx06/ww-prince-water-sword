# Voice coverage — Preview 1

The approved voice payload is unchanged from the installed preview. This release packages it with the existing model and Water Sword; it does not regenerate or reinterpret it.

- 93 isolated spoken Prince lines included, 473.194 seconds total.
- The approved homecoming benchmark (record 270) is retained exactly.
- 17 held spoken candidates remain original: 259, 275, 280, 289, 300, 304, 307, 314, 316, 318, 320, 321, 323, 344, 348, 351, 358.
- 13 ambiguous/nonverbal Prince records remain original: 257, 258, 367–377.
- Mixed-speaker cinematics, other speakers and Dark Prince are not replaced.
- Counts describe the isolated candidate set, not all dialogue in the entire game.

Held clips did not satisfy the current codec-quality gate (>20 dB reconstruction SNR); one regenerated candidate also had a wording discrepancy. They and experimental listening reels are deliberately not installed or distributed here.

The conversion preserves The Two Thrones lines and timing, using situation-matched Warrior Within voice references to guide identity and tone. It is AI-converted audio, not newly recorded dialogue by the original actor. No actor endorsement or authorization is claimed.

Version 0.5.1 is OpenJade-only. Mod Manager adds a compact `wwprince.ls0` stream and replaces the supported English `001.sb0` bank to redirect the 93 selected records. The FAT and BIG layout change; the original external stream remains intact on a clean installation. Unknown original bank hashes are rejected. No voice installer is required. Historical in-place range metadata in `voice/manifest.json` is provenance, not the new archive layout.
