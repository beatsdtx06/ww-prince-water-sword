# Changelog

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
