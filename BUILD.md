# Build the OpenJade-only package

Players only need the release ZIP and Mod Manager. These instructions are for developers.

Use Python 3.11+ and a full clone with history. Extract the original English `sound/english/001.sb0` from your legally owned game using a compatible asset tool; do not use a modified bank.

```powershell
python tools/package_release.py --bank "X:/Extracted/sound/english/001.sb0"
python tools/test_release.py
```

The bank SHA-256 must be `a83de99c058b688e07c944cb97cb1a1dbb2736eefd3486196865afff5db8a3a0`. The build rejects other inputs. It modifies only 93 stream/name references, adds a stream filename to the bank's extra table, and preserves the remaining bank data. The compact stream is made from the exact approved files in `voice/patches/`; no AI regeneration occurs.

The model input is read from commit `649046bac415656de88d1198e4ae3b25013c057d`, path `WW-Prince-Water-Sword-OpenJade-Clean-Start-0.4.0.jtmod`, SHA-256 `b579b7b61a8fb69d0785b636b1b8422918b9b495295d1a814d480aceca410bf0`. Alternatively supply that exact historical file using `--model-input`. No whole BF archive is shipped.

The deterministic build emits `assets/WW-Prince-Model-Sword-Voice-0.5.1.jtmod`, the corresponding ZIP, `package-manifest.json`, an OpenJade-only `pmm_manifest.json` entry, and `SHA256SUMS.txt`. ZIP timestamps are fixed. JTMod v9 uses native stream-add operation 7 and guarded bank-replacement operation 3; no added game files, helper scripts or executable operations are emitted.

`tools/jtmod.py` independently reads the output and reconstructs its model-only v3 view. The historical `source/model-record-sources-0.4.0.zip` is retained for model reconstruction; its historical machine-specific paths need configuration. `source/voice-record-map.json` supplies the exact 93 row mappings.

`voice/manifest.json` describes the accepted historical in-place voice payload ranges for provenance; its whole-archive output hash is not the new native sound-archive hash. Current operation hashes are in `package-manifest.json`.

Historical installers are recoverable from Git/release 0.5.0, but are removed from the current build and player download.
