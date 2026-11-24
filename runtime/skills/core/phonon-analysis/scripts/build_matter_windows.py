"""Build the upstream MatterSim Cython kernel with a pinned user-local C compiler."""
from pathlib import Path, PurePosixPath
import shutil
import subprocess
import sys
import sysconfig
import tarfile
from tempfile import TemporaryDirectory

import numpy
from runtime_assets import install_file

SOURCE = {
    "url": "https://files.pythonhosted.org/packages/fd/d4/860edc78d9f2f0b455cbd9a9a00186845c6b2f3694467ba89091870fa690/mattersim-1.2.2.tar.gz",
    "archive": "mattersim-1.2.2.tar.gz",
    "sha256": "b1ce486d4bc3fae38395dd4b16d21486e012aedcce2fec30994d9a19fb80e6e0",
}


def main(cache):
    archive = cache / "sources" / SOURCE["archive"]
    install_file(SOURCE, archive, True)
    site = Path(sysconfig.get_path("purelib"))
    with TemporaryDirectory(dir=site) as scratch:
        build = Path(scratch)
        package = build / "mattersim"
        with tarfile.open(archive) as upstream:
            for member in upstream:
                parts = PurePosixPath(member.name).parts
                if not member.isfile() or parts[:1] != ("mattersim-1.2.2",) or ".." in parts:
                    continue
                if parts[1:] == ("LICENSE.txt",):
                    target = package / "LICENSE.txt"
                elif parts[1:3] == ("src", "mattersim"):
                    target = package.joinpath(*parts[3:])
                else:
                    continue
                target.parent.mkdir(parents=True, exist_ok=True)
                with upstream.extractfile(member) as src, target.open("wb") as out:
                    shutil.copyfileobj(src, out)
        entry = package / "datasets/utils/threebody_indices.pyx"
        source = build / "threebody_indices.c"
        subprocess.run([sys.executable, "-m", "cython", "-3", "-o", str(source), str(entry)], check=True)
        dll = Path(sys.base_prefix) / f"python{sys.version_info.major}{sys.version_info.minor}.dll"
        output = entry.with_suffix(".pyd")
        command = [sys.executable, "-m", "ziglang", "cc", "-target", "x86_64-windows-gnu", "-O2",
                   "-shared", "-DMS_WIN64", "-DNPY_NO_DEPRECATED_API=NPY_1_24_API_VERSION",
                   "-I" + sysconfig.get_path("include"), "-I" + numpy.get_include(),
                   str(source), str(dll), "-o", str(output)]
        subprocess.run(command, cwd=build, check=True)
        # The environment belongs to this skill runtime; stage all upstream files before publishing.
        destination = site / "mattersim"
        if destination.exists():
            destination.rename(build / "previous")
        try:
            package.rename(destination)
        except OSError:
            if (build / "previous").exists():
                (build / "previous").rename(destination)
            raise


if __name__ == "__main__":
    main(Path(sys.argv[1]))
