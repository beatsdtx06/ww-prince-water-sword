# Warrior Within Prince and Water Sword for The Two Thrones

Version 0.4.0 fixes clean installations: the Water Sword is now equipped from New Game in both supported editions instead of only appearing after the game supplies a primary weapon.

| Edition | Target | Included behavior |
| --- | --- | --- |
| Steam Clean Start | Original Steam release | Warrior Within Prince, separate hair, medallion and Water Sword from New Game; normal damage and story progression. |
| OpenJade Clean Start | OpenJade 0.4.1 | Warrior Within Prince, persistent Water Sword from New Game, enhanced damage and boss-only blue aura. |

Do not install both editions together.

## Steam installation

1. Back up your saves and connect the Steam installation in [PoP Mod Manager](https://github.com/kaminoer/PoP-Mod-Manager).
2. Import `WW-Prince-Water-Sword-Steam-Clean-Start-0.4.0.jtmod` and apply it. Choose **Enable & Apply** when the manager offers large-asset support.
3. Close the game and Mod Manager.
4. Run `Install-Steam-Water-Sword.cmd`. The patcher accepts only the known Mod Manager executable, verifies its stock backup, and creates its own restorable backup before changing one interpreter setting.
5. Launch the game through Steam and start a New Game.

If Steam is installed somewhere unusual, run PowerShell as follows:

```powershell
.\Install-Steam-Water-Sword.ps1 -Action Install -GameDirectory "D:\Path\To\Prince of Persia Two Thrones"
```

To remove the Steam edition, first run `Restore-Steam-Executable.cmd`, then use **Restore original** and disable **Large assets** in Mod Manager.

## OpenJade installation

Import and apply `WW-Prince-Water-Sword-OpenJade-Clean-Start-0.4.0.jtmod` to a stock archive with PoP Mod Manager, then launch it with your separately installed OpenJade 0.4.1 engine. No executable patch is used for OpenJade.

## Supported archive

Stock `pop3.bf`: 497424384 bytes; SHA-256 `00134ea93ccf27f29ede40d3521439ca8f8c0d38bc02fdfd0d18042e7929b600`.

Other archives and overlapping character or weapon replacement mods are unsupported.

## Verification

Both packages pass Mod Manager verification and apply cleanly to the stock archive. The OpenJade result is byte-identical to the previously observed clean-start build. The Steam helper was tested through install, status and restore against the supported Mod Manager executable and restored it byte-for-byte. See `SHA256SUMS.txt` and `CHANGELOG.md`.

`source-code.zip` contains final project metadata, release scripts, proof reports and prior record-level reconstruction sources. No game executable or full game archive is included.
