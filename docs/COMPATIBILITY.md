# Supported target and original hashes

Target: OpenJade The Two Thrones with the supported English data layout.
Tested dependency versions: OpenJade 0.5.1 and PoP Mod Manager 2.1.2.
Original Classic/Steam-engine compatibility is not supported by this release.

The native package requires these exact original English banks:

| Bank | SHA-256 |
| --- | --- |
| `sound/english/001.sb0` | `a83de99c058b688e07c944cb97cb1a1dbb2736eefd3486196865afff5db8a3a0` |
| `sound/english/004.sb0` | `344c400ab5d051501ed5af25d19721f2b871fbc0cf13a263639c205c6ea0bc68` |

An original-hash mismatch is a stop condition, not something to bypass. No
compatibility with arbitrary overlapping mod stacks or other-language banks is
claimed. Current replacement payloads and model fingerprint are recorded in
`package-manifest.json`; installation and runtime limits are in `docs/TESTS.md`.
