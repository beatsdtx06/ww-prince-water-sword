# Supported OpenJade files

OpenJade 0.5.1 with PoP Mod Manager 2.1.2, The Two Thrones PC English assets. Original Steam engine is not supported by this release. No executable changes are performed.

The tested engine identifies itself in-game as OpenJade 0.5.1, commit `3ce8d00b`. Its executable SHA-256 is `44e71fa278d790e61d70203d1555c7a2b7c556a6a64098978cf01b155c5f27d4`. Earlier notes incorrectly called this same binary 0.4.1 based on Windows file metadata; the runtime version is authoritative.

| Asset | SHA-256 |
| --- | --- |
| Original `pop3.bf`, 497424384 bytes | `00134ea93ccf27f29ede40d3521439ca8f8c0d38bc02fdfd0d18042e7929b600` |
| Mod alone applied `pop3.bf`, 603050280 bytes | `3d4b138b0babfe026669db584b5bed29b25ddca94f23172cfa6c30f288c3409d` |
| Original English `001.sb0` | `a83de99c058b688e07c944cb97cb1a1dbb2736eefd3486196865afff5db8a3a0` |
| Native redirected `001.sb0` | `efbe9ce1441782f0d23804ef79619755426dd1072b78dd8fbfb75491a2ed24d3` |
| Added `wwprince.ls0` | `8b2db59b6765d6e0a3019551496991320335b7e67a37558bcbefaefd2ed16315` |
| Original `soundlocal.big`, 92169193 bytes | `7e810ba92128a00d505d1a89cb84adb97553cdc6bf5a8e4e4cf99b5487f9a627` |
| Original `soundlocal.fat` | `ac47195fedeb6edb35ec608022f7713a13908b41a4f948a4587beb2ee26fa972` |

Unlike the old helper, native installation changes sound archive layout and its FAT. All approved clip bytes remain identical; non-target entries and the original `stream.ls0` remain unchanged on a clean original installation. Restore original returns both original sound archives exactly in the tested fixture.

Other languages, unknown bank revisions, arbitrary overlapping sound/model mods and other OpenJade versions are not claimed compatible. Never force past a hash or integrity error. Mod Manager's catalog marks this package `targets: openjade`; manual import is not an engine-compatibility guarantee.
