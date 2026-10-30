# Details — 0.6.0

## Contents

The JTMod is the only release file. It contains:

- 61 `pop3.bf` model/script record edits (model, Water Sword, damage, aura)
- `sound/english/wwprince.ls0`: voice stream
- `sound/english/001.sb0`: dialogue bank pointing selected lines to that stream
- `sound/english/004.sb0`: resident bank with native WW efforts

No game executable, DLL, whole archive, source audio or AI model is shipped.
Payload hashes: [package-manifest.json](../package-manifest.json).

## Voice coverage

| Category | Count |
| --- | ---: |
| Isolated Prince dialogue clips | 110 |
| Prince lines inside in-engine scenes | 80 (across 38 scene tracks) |
| Native WW efforts (bank 004) | 26 |
| Native WW death/fall sounds (bank 001) | 2 |

Dialogue is AI voice conversion (Seed-VC) of the TTT lines with the WW voice,
keeping TTT wording and timing. Efforts and death/fall sounds are original WW
recordings. Unchanged: pre-rendered videos, the Dark Prince, other characters,
and 21 nonverbal sounds with no reliable mapping.

## Required original banks

| Bank | SHA-256 |
| --- | --- |
| `sound/english/001.sb0` | `a83de99c058b688e07c944cb97cb1a1dbb2736eefd3486196865afff5db8a3a0` |
| `sound/english/004.sb0` | `344c400ab5d051501ed5af25d19721f2b871fbc0cf13a263639c205c6ea0bc68` |

Mod Manager refuses to apply on a mismatch. Do not bypass it.

## Known limits

- One short interrupted word in the Babylon flashback is unclear.
- The repaired phrase "what of" uses a crossfaded donor phrase.
- No full-campaign playthrough or full listening pass has been done.
- The four corrected hurt sounds and two death/fall sounds are checked offline, not individually triggered in game.

## Testing

- **Offline:** package integrity, all 61 model records, bank guards, and full
  decode/PCM checks on all new audio records.
- **Install:** sound archive apply, byte-exact restore and reapply on verified
  originals (archive-level, not a Mod Manager UI run of the final file).
- **In game (2026-10-29):** final package loaded on OpenJade 0.5.1 Vulkan from a
  test save; WW Prince and Water Sword visible, about 60 FPS, no errors logged.
  Earlier builds were user-tested for New Game Water Sword, opening dialogue
  and WW efforts.

## Verify the download

Python 3.11+, no dependencies:

```
python tools/verify.py --self-test
python tools/verify.py --artifact path/to/WW-Prince-Model-Sword-Voice-0.6.0.jtmod
```

Checks the hash, model fingerprint, native operations and bank guards against
`package-manifest.json`. Offline only; it does not touch the game.
Expected SHA-256 is in [SHA256SUMS.txt](../SHA256SUMS.txt).
