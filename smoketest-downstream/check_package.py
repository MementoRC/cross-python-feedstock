# Checks the cross-built downstream package: the extension is there with the
# target suffix and machine, and the host python.exe that the activation
# swapped for the wrapper did not leak into it.
# usage: python -I check_package.py <output/win-64>
import io
import pathlib
import struct
import sys
import tarfile
import zipfile

import zstandard

IMAGE_FILE_MACHINE_AMD64 = 0x8664
EXPECTED_PYD = "Lib/site-packages/smoke.cp314-win_amd64.pyd"


def pe_machine(data):
    (pe,) = struct.unpack_from("<I", data, 0x3C)
    assert data[pe:pe + 4] == b"PE\0\0", "not a PE file"
    (machine,) = struct.unpack_from("<H", data, pe + 4)
    return machine


(pkg,) = pathlib.Path(sys.argv[1]).glob("cross-python-smoke-*.conda")
print(pkg)
with zipfile.ZipFile(pkg) as z:
    (inner,) = [n for n in z.namelist() if n.startswith("pkg-") and n.endswith(".tar.zst")]
    reader = zstandard.ZstdDecompressor().stream_reader(io.BytesIO(z.read(inner)))
    names, pyds = [], {}
    with tarfile.open(fileobj=reader, mode="r|") as tar:
        for member in tar:
            names.append(member.name)
            if member.name.endswith(".pyd"):
                pyds[member.name] = tar.extractfile(member).read()

for name in names:
    print("  " + name)
leaked = [n for n in names if pathlib.PurePosixPath(n).name.lower().startswith(("python.exe", "pythonw.exe"))]
assert not leaked, f"host python leaked into the package: {leaked}"
assert list(pyds) == [EXPECTED_PYD], f"expected only {EXPECTED_PYD}, got {list(pyds)}"
machine = pe_machine(pyds[EXPECTED_PYD])
print(f"{EXPECTED_PYD}: machine 0x{machine:04X}")
assert machine == IMAGE_FILE_MACHINE_AMD64, "not an x86-64 extension"
print("downstream package OK")
