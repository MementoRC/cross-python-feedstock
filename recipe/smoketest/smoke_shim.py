# T5: a downstream recipe script runs ${{ PYTHON }}, which renders to the
# literal %PREFIX%\python.exe of the target python and cannot run on the build
# machine. After activation that path must still reach the build python.
# A junk python.exe stands in for the arm64 one (error 193 instead of 216).
# Expected to fail until the x64 launcher shim lands; pass --strict after.
# usage: python smoke_shim.py <activate.bat> <deactivate.bat> [--strict]
import os
import subprocess
import sys
import tempfile

activate, deactivate = sys.argv[1], sys.argv[2]
strict = "--strict" in sys.argv[3:]
build_python = os.path.join(sys.prefix, "python.exe")

with tempfile.TemporaryDirectory() as tmp:
    host = os.path.join(tmp, "host")
    os.makedirs(os.path.join(host, "include"))
    os.makedirs(os.path.join(host, "libs"))
    fake = os.path.join(host, "python.exe")
    with open(fake, "wb") as f:
        f.write(b"not a windows executable")
    probe = os.path.join(tmp, "probe.bat")
    with open(probe, "w") as f:
        f.write("@echo off\n")
        f.write(f'call "{activate}"\n')
        f.write(f'"{fake}" -c "import sys; print(sys.executable)"\n')
        f.write("set RC=%ERRORLEVEL%\n")
        f.write(f'call "{deactivate}"\n')
        f.write("exit /b %RC%\n")
    env = dict(os.environ, PREFIX=host, BUILD_PREFIX=sys.prefix, CONDA_BUILD="1")
    env.pop("CONDA_BUILD_STATE", None)
    res = subprocess.run(["cmd", "/d", "/c", probe], env=env, capture_output=True, text=True)

out = res.stdout.strip().splitlines()
ok = res.returncode == 0 and out and os.path.normcase(out[-1]) == os.path.normcase(build_python)
if ok:
    print(f"T5 OK: %PREFIX%\\python.exe reached {out[-1]}")
    if not strict:
        print("T5 XPASS: the shim works, pass --strict to smoke_shim.py")
    sys.exit(0)
print(f"rc={res.returncode}\nstdout={res.stdout}\nstderr={res.stderr}")
if strict:
    sys.exit(1)
print("T5 XFAIL: %PREFIX%\\python.exe does not reach the build python yet")
