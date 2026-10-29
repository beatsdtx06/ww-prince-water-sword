# English voice coverage — 0.6.0

| Category | Included |
| --- | ---: |
| Isolated spoken Prince clips | 110 |
| Mapped Prince turns in mixed in-engine scenes | 80 |
| Mixed scene tracks containing those turns | 38 |
| Native WW effort resources in bank 004 | 26 |
| Native WW death/fall sounds in bank 001 | 2 |

These are resource counts, not unique sentences, seconds or an assertion of
100% campaign coverage. The 110 isolated spoken clips comprise the original 93
approved clips plus the 17 previously held spoken clips, now validated. The
tested opening shout, homecoming and first weapon-pickup dialogue are retained.
The active homecoming record 270 uses the later approved PCM replacement; the
historical 93 encoded payload bytes remain in the stream but are not all active.
The 80 scene turns include the two tested opening tracks, not 80 additional
tracks. A track may contain multiple characters or multiple Prince turns.

Scene processing targets only mapped normal-Prince intervals. Original samples
outside those intervals are preserved; protected Dark Prince and other-speaker
turns are not converted. The converted speech follows TTT lines and preserves
slot timing while using the approved WW voice identity/expression balance;
narrow wording uncertainties are documented below. The 26 gameplay effort
resources use original WW recordings, not the rejected AI grunt generation.

The two mapped death/fall sounds use complete original WW recordings resampled
to the original TTT sample rate, with trailing silence to preserve exact slot
duration. No voiced portion is trimmed, and no speed or pitch shift is applied.

Four resident effort slots use native WW hurt recordings after event-selector
review. The accepted short attack resources remain short; the rejected long
attack-tail experiment is not included.

## Intentional exclusions and remaining limits

- Pre-rendered video audio remains original.
- The Dark Prince and other characters remain original.
- Eight additional resources reached through normal-Prince branches remain original because their action-specific replacement mapping is unresolved; 13 further unclassified nonverbal resources also remain original. No unknown resource is guessed into the pack.
- Only the supported English audio layout is targeted.
- Offline checks and scoped gameplay tests do not substitute for a complete campaign playthrough.

See `package-manifest.json` for the packaged record/hash inventory and
`docs/TESTS.md` for test scope. No extracted original voice files or AI weights are
required by players or the public ZIP-repackaging tool.

## Current release-specific limitations

- One very short interrupted final of in the Babylon reminiscence has uncertain articulation; automatic recognition omits it. This is not a verbatim-perfect or full-campaign listening certification.
- The what-of repair uses an accepted same-voice phrase with a short coarticulated entry crossfade. Recognition differs by model; exact provenance and reconstruction were checked.
- Eight additional known-normal-Prince nonverbal resources lack reliable action-specific replacement mapping; 13 further nonverbal resources remain unclassified. They are intentionally left original.
- Pre-rendered video audio, the Dark Prince and other speakers remain original. Only the supported English audio layout on OpenJade is targeted.
- No complete campaign playthrough or final-package subjective listening certification is claimed. The final four hurt-slot corrections and two death/fall mappings have offline provenance/format checks, not individual in-game trigger confirmation.
