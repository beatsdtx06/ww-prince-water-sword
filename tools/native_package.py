"""Historical 0.5.1 synthesis entry point retired to prevent stale rebuilds.

The old implementation remains in Git history. Current public packaging verifies
and repackages the approved combined asset with tools/package_release.py.
"""


def native_package(*args, **kwargs):
    raise RuntimeError('The historical 0.5.1 synthesizer is retired. Use package_release.py '
                       'to verify/repackage the approved 0.6.0 JTMod; see BUILD.md.')


if __name__ == '__main__':
    raise SystemExit('No synthesis is performed. See BUILD.md and tools/package_release.py.')
