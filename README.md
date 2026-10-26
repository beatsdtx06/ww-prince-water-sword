# Warrior Within Prince and Water Sword for The Two Thrones

Two editions prepared by **beatsdtx06**. Choose the edition matching your game.

| Edition | Supported target | Features |
| --- | --- | --- |
| Steam Visuals 0.3.0-rc4 | Original Steam release, with PoP Mod Manager's built-in large asset support | Warrior Within Prince, separate hair, chest medallion, Water Sword appearance and accepted visual animations. Normal game damage and story weapon progression. |
| OpenJade Full 0.3.0-rc3 | OpenJade 0.4.1 | Prince model, persistent right-hand Water Sword, enhanced damage and boss-only blue aura. |

**Steam Visuals has no enhanced damage, boss aura, or sword during the unarmed opening.** Do not install both editions together. OpenJade Full does not support the original Steam executable.

## Install

1. Back up your saves and connect your game installation in [PoP Mod Manager](https://github.com/kaminoer/PoP-Mod-Manager).
2. Add this repository in the manager's repository view, or download the matching `.jtmod` from this repository and import it locally.
3. Select only the matching edition and apply. For Steam, accept **Enable & Apply** when the manager offers large asset support.
4. Launch the original Steam game through Steam. For the full edition, use your separately installed OpenJade 0.4.1 engine.

Our packages contain no custom runtime DLL, executable, launcher, Dahaka controller or Tab wheel. Steam's required large asset support is supplied by the manager itself; it modifies the executable and adds the manager's own support DLL. It is not bundled in our mod.

## Supported archive

Stock `pop3.bf`: 497424384 bytes, SHA-256:
`00134ea93ccf27f29ede40d3521439ca8f8c0d38bc02fdfd0d18042e7929b600`.

Other archives are unsupported. Do not bypass hash checks or combine overlapping character/weapon replacements.

## Remove

Use **Restore original** in Mod Manager. To restore the original Steam executable too, disable **Large assets**. The manager may retain its support DLL and executable backup. Steam verification does not remove extra files. Keep backups and do not delete unknown files or personal saves.

## Validation

The corrected Steam edition was imported and applied through standard Mod Manager, launched through Steam, and loaded into gameplay. The Prince, hair and sheathed Water Sword were observed; the user confirmed the remaining front/drawn-sword visual check. Removal restored every one of the 191 Steam-owned files exactly. Test-generated files were preserved outside the installation, leaving zero extras.

The full OpenJade edition retains previously accepted gameplay behavior. This is not a claim that every possible save, mod combination or campaign state has been retested. RC4 fixes a resource ordering error in the earlier Steam RC3 split; use RC4 for Steam.

## Source and notices

`source-code.zip` contains maintained build inputs and review materials. See [BUILD.md](BUILD.md) for reproducible package construction, and [NOTICES.md](NOTICES.md) for provenance. No game executable or full game archive is included. Checksums are listed in `SHA256SUMS.txt`.
