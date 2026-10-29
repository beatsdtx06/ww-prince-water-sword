# Build notes

`source-code.zip` contains the compact record-level sources from the prior release line plus the 0.4.0 clean-start transformation, final Jade Toolkit project metadata, executable patch source, proof report and verification report.

The exact 0.4.0 export process is documented in `release-tools/build_release.py`: export the final Jade Toolkit projects against the supported stock archive, annotate minted keys, verify each package with PoP Mod Manager, apply it to stock, and compare the resulting archive scope and hashes. Local tool and archive paths in the script must be adjusted for another checkout.

Raw game-derived Jade project assets, the stock archive, the game executable and third-party build tools are not redistributed. The compact `Steam-Visuals` and `OpenJade-Full` folders preserve the record-level reconstruction and readable script history; `make_steam_clean_project.py` documents the 0.4.0 Steam transformation.

The Steam executable helper is ordinary PowerShell source. It changes only the 32-bit value at file offset `0x5E1380`, and only after exact executable and backup hash checks. Its supported input/output hashes are embedded in the script.
