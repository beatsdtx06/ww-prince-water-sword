# Verify and repackage the approved release

Players need only the release ZIP and Mod Manager. Download that ZIP (or the raw
JTMod) from the GitHub release first. It is a release asset, not part of a Git
clone. Developers can then use Python 3.11+ (standard library only):

```powershell
python tools/test_release.py --self-test
python tools/test_release.py --artifact downloads/WW-Prince-Model-Sword-Voice-0.6.0.zip
python tools/package_release.py --artifact downloads/WW-Prince-Model-Sword-Voice-0.6.0.zip --out dist/WW-Prince-Model-Sword-Voice-0.6.0.zip
python tools/test_release.py --artifact downloads/WW-Prince-Model-Sword-Voice-0.6.0.jtmod --zip dist/WW-Prince-Model-Sword-Voice-0.6.0.zip
```

Use the actual path where you saved the download; either ZIP or JTMod is accepted
by `--artifact`. Nothing is downloaded automatically. ZIP input is read and
validated in memory, not extracted into the repository. The packager validates
the JTMod integrity trailer, complete file SHA-256, game/version, 61 model
operations, metadata-independent model fingerprint, three native operations,
original-bank guards, embedded payload hashes, empty manual-import catalog and player-doc
hashes. ZIP contents and timestamps are fixed. It refuses to overwrite an
existing output; choose a new output path when comparing builds.

It does **not** regenerate voice conversions, rebuild game banks from source,
change manifests, patch an installation, or update the repository. A clean public
clone alone cannot produce a mod binary: the hash-matching downloaded release
asset is required. These tools can repackage that existing asset, not regenerate
the JTMod from private voice-processing inputs. No API, source game audio or AI
model is a public-repackaging dependency.

The old 0.5.1 93-line synthesizer is retired. `tools/native_package.py` now refuses
synthesis so stale scripts cannot silently overwrite the expanded release. Its
historical implementation and the old development payloads remain recoverable
from Git history; they are not current player dependencies.
The historical model reconstruction archive is likewise recoverable from old
commits. `source/voice-record-map.json` is retained as historical row provenance
for internal preservation checks, not as a recipe for rebuilding this release.

The production JTMod was assembled by a separate offline, hash-bound workflow:
the accepted base dialogue and tested opening edits were retained (including the
later approved PCM homecoming, record 270, rather than its historical encoding);
new speech received wording, timing, PCM-format and decoder checks; other scene
speakers and protected samples were checked; native efforts were rebuilt from
original WW PCM with preservation checks. Those checks are described in
`docs/TESTS.md`, not re-run by this public repackager.
