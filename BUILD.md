# Build the single JTMod

Player download: `assets/WW-Prince-Model-Sword-Voice-0.5.0.jtmod`. No ZIP or edition-specific player packages are produced.

With Python 3.11+ and a full Git clone:

```powershell
python tools/package_release.py
python tools/test_voice_installer.py
python tools/test_release.py
```

The deterministic packager reads the accepted Steam model/sword input from Git commit `649046bac415656de88d1198e4ae3b25013c057d`, path `WW-Prince-Water-Sword-Steam-Clean-Start-0.4.0.jtmod`, and verifies its exact SHA-256. Alternatively pass `--model-input PATH` to that exact historical file. Historical binaries are not duplicated among current player downloads.

It re-encodes unchanged BF edits into JTMod v9, adds the allowlisted setup files, deduplicates raw payloads, and writes the format integrity trailer. It regenerates `package-manifest.json`, the single `targets: both` catalog entry, and `SHA256SUMS.txt`. Rebuild after editing any embedded file. These checksums detect accidental corruption, not malicious replacement of the manifest.

`tools/jtmod.py` independently reads the produced subset, checks safe paths/integrity, and reconstructs a v3 model-only view for comparison and legacy CLI testing. Mod Manager 2.1.2 reads v9; the historical C++ CLI does not.

`installers/openjade-effects.delta.gz` maps the exact accepted Steam-applied archive to the exact accepted OpenJade-applied archive using bounded copy/literal operations. It contains no complete BF archive. Rebuild it only from locally owned, hash-matching inputs:

```powershell
g++ -O2 -std=c++17 tools/make_delta.cpp -o make_delta.exe
python tools/build_effects_delta.py STEAM-APPLIED.bf OPENJADE-APPLIED.bf --encoder ./make_delta.exe
```

The C++ encoder is development-only; neither it nor a compiler is included in the JTMod. Player setup uses built-in PowerShell/.NET gzip decoding and verifies the complete output before atomic replacement. The copy/literal instructions are portable little-endian.

`source/model-record-sources-0.4.0.zip` preserves the previous public reconstruction source, including historical machine-specific paths that developers must configure. Current runtime scripts have no private workstation paths. `voice/` contains the complete approved 93 payloads and reversible installer; private reference recordings, inference environments and AI weights are excluded. Regeneration of identical AI audio is not claimed.

`tools/test_release.py --help` lists optional real-archive inputs for disposable integration tests. No installed game is modified by these tests. `docs/TESTS.md` records the scope and limits.
