# Changelog

## 0.5.1 - 2026-10-29

- OpenJade-only release; dropped original Steam-engine support as requested.
- Replaced the helper-based workflow with native Mod Manager operations: extract ZIP, import one JTMod, Apply, launch.
- Included the accepted full OpenJade model/sword/effects records directly, retaining enhanced damage and boss-only blue aura.
- Kept all 93 approved voice payloads byte-for-byte; added a compact voice stream and guarded bank redirection.
- Verified native Apply, exact Restore original, and reapply in a disposable copy.
- Removed obsolete helper scripts, Steam installers, delta tools and old player binary from the current repository tree. They remain recoverable in Git/release history.
- Added a clean player ZIP, OpenJade-only catalog targeting, native operation manifest and revised installation/compatibility documentation.

## 0.5.0 - 2026-10-29

- Combined the WW Prince model, New Game Water Sword and approved 93-line Prince voice preview into exactly one universal JTMod for Steam and OpenJade.
- Preserved each edition's accepted 0.4.0 model/sword output and all approved voice bytes. OpenJade keeps enhanced damage and boss-only blue aura.
- Embedded a Finish Setup launcher, reversible edition-specific helpers, voice patches and complete file manifest using JTMod v9 added files. Finish Setup remains required after Apply.
- Organized assets, shared voice patches, installers, documentation, source and tests.
- Removed obsolete root launchers from the current release; previous files remain recoverable in Git history.
- Excluded original archives, backups, local paths in current voice metadata, failed voice experiments, AI weights and development clutter from the player download.
- Documented every required file, partial voice coverage, compatibility, installation order and recovery.

## 0.4.0 - 2026-10-29

- Fixed clean installations starting with the Warrior Within Prince model but no Water Sword.
- Added the guarded clean-start Water Sword grant to the Steam package's 12 Prince frame providers.
- Added a reversible, exact-hash-checked Steam interpreter patch so the original executable runs the package scripts.
- Published the OpenJade clean-start package that equips the Water Sword from New Game.
- Updated install, removal, build and checksum documentation.

## 0.3.0 release candidates

- Published separate Steam visual and OpenJade full editions.
- The Steam edition only reskinned a primary weapon once normal story progression supplied one; this limitation is corrected in 0.4.0.
