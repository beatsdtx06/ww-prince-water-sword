# Exact supported files

Model/sword input: stock pop3.bf, 497424384 bytes.

`00134ea93ccf27f29ede40d3521439ca8f8c0d38bc02fdfd0d18042e7929b600`

After the Steam JTMod:

`cb9424bf647d6a3eac08ab139dbc68ae4024378ef43c43f00f18c8ab8a1c4644`

After the OpenJade JTMod:

`3d4b138b0babfe026669db584b5bed29b25ddca94f23172cfa6c30f288c3409d`

English Sound/soundlocal.big: 92169193 bytes, original:

`7e810ba92128a00d505d1a89cb84adb97553cdc6bf5a8e4e4cf99b5487f9a627`

With the approved 93-line voice patch:

`67459b29e5cb349d60b8165822e79bfd9a078ea98213ee9e1677d93f765e0dc8`

Sound/soundlocal.fat (never modified):

`ac47195fedeb6edb35ec608022f7713a13908b41a4f948a4587beb2ee26fa972`

Steam POP3.EXE stock:

`febbabb37d355ebbe51c4e8cd4172ad825870c759b529421f361a13339aa0941`

After Mod Manager Large assets:

`f42f721f1394894b87b4584ca1e9bc0c2be7af71cf39a1a3548925fa9eab7cfa`

After the interpreter helper:

`f6dd6820334918d915c8d6b70a60b799d3e85b3be9c5a3245d240768be734208`

The helper changes the known 32-bit interpreter flag at offset 0x5E1380 from 1 to 0 only on the exact supported executable. OpenJade does not need this patch. Do not apply it to OpenJade.

Other language banks, executables, archive revisions, overlapping mods and engines other than the tested OpenJade 0.4.1 are not claimed compatible. Do not bypass hash checks to force installation.
