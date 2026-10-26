# Reproduce the packages

Extract source-code.zip first; it contains the source/ folder shown below.

Python 3.15 tested; standard library only. No compiler, pip dependency, LZO decoder or Jade archive parser is bundled or required.

```powershell
python source/Steam-Visuals/build.py --base "PATH/TO/STOCK/pop3.bf" --out "NEW/steam-build"
python source/OpenJade-Full/build.py --base "PATH/TO/STOCK/pop3.bf" --out "NEW/openjade-build"
```

The stock archive is read only to validate its size and SHA-256. `delta-recipe.json` defines ordered record replacements; `delta-records/` supplies their bytes. Each record and final package hash is checked before output. Unsupported archives, corrupted inputs and existing output directories are rejected. This is a package reconstruction pipeline, not a complete artistic-source pipeline.

`manifest.json`, `records/`, and the OpenJade script constructors/disassemblies preserve development review material. The authoritative package inputs are the delta recipe and delta records. Resource ordering is significant: imported resources must stay in their appropriate stream sections, ahead of the end marker. The Steam RC4 rebuild was reproduced twice identically.

Expected hashes are in `pmm_manifest.json`. Only the two `.jtmod` files are installed into the game through the manager; the Python sources are optional build/review materials and are not executed during mod installation.
