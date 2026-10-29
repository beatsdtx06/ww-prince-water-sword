"""Strict, read-only parser for this release's raw-payload JTMod v9 subset.

Validation uses exceptions rather than assertions, including under Python -O.
The reader never extracts embedded paths or mutates a game installation.
"""
import hashlib
import re
import struct
from pathlib import PurePosixPath


def require(ok, message):
    if not ok:
        raise ValueError(message)


def digest(data):
    return hashlib.sha256(data).hexdigest()


def u32(value):
    return struct.pack('<I', value)


def blob(value):
    if isinstance(value, str):
        value = value.encode('utf-8')
    return u32(len(value)) + value


def seal(core):
    return core + b'JTMHASH1' + hashlib.sha256(b'jtmod-integrity-v1' + core).digest()


def unseal(data):
    require(len(data) >= 56 and data[-40:-32] == b'JTMHASH1', 'Missing JTMod integrity trailer')
    require(hashlib.sha256(b'jtmod-integrity-v1' + data[:-40]).digest() == data[-32:],
            'JTMod integrity mismatch')
    return data[:-40]


class Reader:
    def __init__(self, data):
        self.data, self.pos = data, 0

    def take(self, count):
        require(type(count) is int and 0 <= count <= len(self.data) - self.pos, 'Truncated JTMod')
        value = self.data[self.pos:self.pos + count]
        self.pos += count
        return value

    def u32(self):
        return struct.unpack('<I', self.take(4))[0]

    def blob(self):
        return self.take(self.u32())

    def count(self):
        value = self.u32()
        require(value <= len(self.data) - self.pos, 'Impossible JTMod item count')
        return value


def model_fingerprint(decoded):
    """Metadata-independent commitment to all model operations and prerequisites."""
    material = (blob(decoded['game']) + blob(decoded['archive']) + decoded['base']
                + blob(decoded['keys']) + u32(decoded['binCount'])
                + b''.join(blob(entry) for entry in decoded['bins']))
    return digest(material)


def read_v9(data):
    reader = Reader(unseal(data))
    require(reader.take(8) == b'JADEJTM1', 'Unexpected JTMod magic')
    require(reader.u32() == 9 and reader.u32() == 0, 'Expected uncompressed JTMod v9')
    game, archive, base = reader.blob(), reader.blob(), reader.take(40)
    metadata = [reader.blob() for _ in range(6)]
    image = reader.blob()
    keys = reader.take(reader.count() * 4)
    payloads = []
    for _ in range(reader.count()):
        require(reader.take(1) == b'\0', 'Compressed payloads are not supported')
        size = reader.u32()
        require(reader.u32() == size, 'Raw payload size mismatch')
        payloads.append(reader.take(size))

    def payload():
        index = reader.u32()
        require(index < len(payloads), 'Invalid payload reference')
        return payloads[index]

    bins = []
    for _ in range(reader.count()):
        entry = reader.take(5)
        mode = entry[-1]
        if mode == 1:
            entry += reader.take(36)
            count = reader.count()
            entry += u32(count)
            for _ in range(count):
                entry += reader.take(8)
                subcount = reader.count()
                entry += u32(subcount)
                for _ in range(subcount):
                    entry += blob(payload())
        elif mode == 2:
            entry += blob(payload())
        elif mode == 3:
            entry += blob(reader.blob()) + reader.take(4) + blob(payload())
        else:
            raise ValueError('Unexpected model operation')
        bins.append(entry)

    files, operations = {}, []
    for _ in range(reader.count()):
        mode = reader.take(1)[0]
        require(mode in (3, 7), 'Only native guarded replacements and additions are allowed')
        path = reader.blob().decode('utf-8')
        pure = PurePosixPath(path)
        require(path and not pure.is_absolute() and '..' not in pure.parts
                and ':' not in path and '\\' not in path and str(pure) == path
                and path not in files, 'Unsafe or duplicate embedded path')
        external_archive, alias, original = reader.blob(), reader.blob(), reader.blob()
        require(external_archive == b'soundlocal' and alias == b'', 'Unexpected native archive')
        require((mode == 7 and original == b'') or
                (mode == 3 and re.fullmatch(b'[0-9a-f]{64}', original)), 'Invalid original hash guard')
        files[path] = payload()
        operations.append(dict(mode=mode, path=path, archive=external_archive.decode(),
                               originalSha256=original.decode()))
    require(reader.pos == len(reader.data), 'Unexpected trailing content')
    count = len(bins)
    model = (b'JADEJTM1' + u32(3) + u32(0) + blob(game) + blob(archive) + base
             + b''.join(blob(value) for value in metadata) + blob(image)
             + u32(len(keys) // 4) + keys + u32(count) + b''.join(bins))
    return dict(game=game, archive=archive, files=files, operations=operations,
                binCount=count, modelV3=seal(model), base=base, metadata=metadata,
                bins=bins, keys=keys)
