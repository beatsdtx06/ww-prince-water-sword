# Verification scope

The package preserves the accepted OpenJade 0.4.0 model/sword/effects records exactly and all 93 approved voice payloads exactly. Historical model behavior evidence is retained in `model-verification-0.4.0.json`; it is not a new campaign test.

Automated release checks cover JTMod integrity, the two native audio operations, original-bank guard, exact accepted BF records, all 93 clip hashes and mappings, held-clip exclusion, one OpenJade-only catalog entry, ZIP contents and hashes, no setup/game-file/executable operations, and deterministic rebuilding.

Private real-manager evidence covers importing and applying the native package, exact modded BF and per-sound-entry comparisons, all 93 full audio decodes, and a GUI Restore original followed by Apply. Original `pop3.bf`, `soundlocal.big` and `soundlocal.fat` hashes were restored exactly. OpenJade 0.5.1 reached gameplay with the WW Prince and Water Sword in the native test copy. Earlier notes used stale Windows version metadata for that same engine binary; see compatibility details.

Current final-artifact checks and their precise limits are recorded in `release-verification.json`. A full campaign, every line's subjective playback, every boss encounter, arbitrary mod combinations, other languages and other engine revisions are not claimed verified. The Steam engine is explicitly outside release scope.

Tests use disposable copies and do not overwrite the user's installed games or saves. Release validation does not require or install an API key, AI runtime, custom launcher, or player-side helper.
