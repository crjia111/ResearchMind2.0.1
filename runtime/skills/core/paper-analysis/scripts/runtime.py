"""Run one ResearchMind operation from this skill's installed directory."""
import argparse
from contextlib import contextmanager
import hashlib
import json
import os
from pathlib import Path
import platform
import shutil
import subprocess
import sys
import time

from runtime_assets import architecture, digest, option, prepare

SCRIPTS = Path(__file__).resolve().parent
ROOT = SCRIPTS.parent
CONFIG = json.loads((ROOT / "references/runtime.json").read_text(encoding="utf8"))


def cache_root():
    base = os.getenv("LOCALAPPDATA") if os.name == "nt" else os.getenv("XDG_CACHE_HOME")
    return Path(os.getenv("RM_CACHE_DIR") or Path(base or Path.home() / ".cache") / "researchmind").resolve()


@contextmanager
def installation_lock(cache):
    cache.mkdir(parents=True, exist_ok=True)
    with (cache / "install.lock").open("a+b") as stream:
        if os.name == "nt":
            import msvcrt
            if stream.tell() == 0:
                stream.write(b"0")
                stream.flush()
            deadline = time.monotonic() + 1800
            while True:
                stream.seek(0)
                try:
                    msvcrt.locking(stream.fileno(), msvcrt.LK_NBLCK, 1)
                    break
                except OSError:
                    if time.monotonic() >= deadline:
                        raise TimeoutError("Timed out waiting for another installation")
                    time.sleep(0.25)
        else:
            import fcntl
            fcntl.flock(stream.fileno(), fcntl.LOCK_EX)
        yield  # Closing the handle releases the lock, including on exceptions.


def document_profile(args):
    parser = argparse.ArgumentParser(add_help=False, allow_abbrev=False)
    parser.add_argument("--input", nargs="+", default=[])
    parser.add_argument("--papers", type=Path)
    parser.add_argument("--paper-id", nargs="+")
    options, _ = parser.parse_known_args(args)
    paths = list(options.input)
    if options.papers and options.papers.is_file():
        rows = json.loads(options.papers.read_text(encoding="utf-8-sig"))
        for row in rows.get("papers", []) if isinstance(rows, dict) else rows:
            if options.paper_id and row.get("paper_id") not in options.paper_id:
                continue
            if row.get("content_file"):
                paths.append(str(options.papers.parent / row["content_file"]))
            if row.get("pdf_url"):
                paths.append("remote.pdf")
    formats = set()
    for path in paths:
        suffix = Path(path).suffix.lower()
        if suffix == ".pdf":
            formats.add("pdf")
        elif suffix == ".docx":
            formats.add("docx")
        elif Path(path).is_file():
            with open(path, "rb") as stream:
                if stream.read(5) == b"%PDF-":
                    formats.add("pdf")
    if len(formats) > 1:
        return "documents"
    return next(iter(formats), None)


PROBES = {
    "pdf": "import pypdf, fontTools",
    "docx": "from docx import Document",
    "documents": "import pypdf, fontTools, docx",
    "materials": "from pymatgen.core import Structure",
    "ase": "from ase.io import read",
    "crystal": "import torch, scipy, pandas; from pymatgen.core import Structure; assert torch.ones(1).item()==1",
    "matter": "from mattersim.forcefield import MatterSimCalculator; from mattersim.datasets.utils import threebody_indices; import phonopy, seekpath, matplotlib",
    "chroma": "import chromadb, pypdf, docx",
}


def find_uv():
    path = shutil.which("uv")
    if path:
        return path
    if os.name == "nt":
        cmd = [shutil.which("pwsh") or "powershell", "-NoProfile", "-File", str(SCRIPTS / "run.ps1")]
    else:
        cmd = ["sh", str(SCRIPTS / "run.sh")]
    return subprocess.check_output(cmd + ["_ensure_uv"], text=True).strip()


def check_python(executable, profile, device, inventory=None):
    if not Path(executable).is_file():
        return False
    probe = PROBES[profile]
    if device == "cuda":
        probe += "; import torch; assert torch.cuda.is_available(), 'CUDA unavailable'"
    if inventory is not None:
        probe += ("\nimport json, sys, importlib.metadata as md\n"
                  "from pathlib import Path\n"
                  "packages = {d.metadata['Name']: d.version for d in md.distributions()}\n"
                  "record = Path(sys.argv[1])\n"
                  "if sys.argv[2] == 'write': record.write_text(json.dumps(packages), encoding='utf8')\n"
                  "else: assert packages == json.loads(record.read_text(encoding='utf8'))")
    return subprocess.run([str(executable), "-B", "-c", probe, *(inventory or ())], stdout=subprocess.DEVNULL,
                          stderr=subprocess.DEVNULL).returncode == 0


def environment(profile, device, cache, repair):
    if not profile:
        return Path(sys.executable), []
    supplied = os.getenv("RM_SCIENCE_PYTHON")
    if supplied:
        python = Path(supplied).resolve()
        if not check_python(python, profile, device):
            raise ValueError("RM_SCIENCE_PYTHON failed the " + profile + " capability check")
        return python, []
    if device == "cuda":
        raise ValueError("Supply RM_SCIENCE_PYTHON with a working CUDA PyTorch installation, or select --device cpu")
    key = (platform.system(), architecture())
    if key not in {("Windows", "amd64"), ("Linux", "x86_64"), ("Darwin", "arm64")}:
        raise ValueError("Use RM_SCIENCE_PYTHON on this platform: " + str(key))
    project = ROOT / "references/locks" / profile
    fingerprint = hashlib.sha256((digest(project / "uv.lock") + digest(project / "pyproject.toml") +
                                  str(key)).encode()).hexdigest()[:16]
    location = cache / "envs" / (profile + "-" + fingerprint)
    python = location / ("Scripts/python.exe" if os.name == "nt" else "bin/python")
    record = location / ".ready"
    if record.is_file() and check_python(python, profile, device, (str(record), "read")):
        return python, []
    if repair:
        env = dict(os.environ, UV_PROJECT_ENVIRONMENT=str(location))
        env.setdefault("UV_CACHE_DIR", str(cache / "uv-cache"))
        env.setdefault("UV_PYTHON_INSTALL_DIR", str(cache / "python"))
        py = os.getenv("RM_PYTHON_312") or (sys.executable if sys.version_info[:2] == (3, 12) else "3.12")
        cmd = [find_uv(), "sync", "--project", str(project), "--frozen", "--no-install-project", "--python", py]
        if record.is_file() and record.stat().st_size:
            cmd.append("--reinstall")
        subprocess.run(cmd, env=env, check=True, stdout=sys.stderr)
        if os.name == "nt" and profile == "matter":
            env.setdefault("ZIG_GLOBAL_CACHE_DIR", str(cache / "zig"))
            subprocess.run([str(python), "-B", str(SCRIPTS / "build_matter_windows.py"), str(cache)],
                           check=True, env=env, stdout=sys.stderr)
        if not check_python(python, profile, device, (str(record), "write")):
            raise RuntimeError("Installed " + profile + " failed its native/import capability check")
        return python, []
    return python, ["Python environment: " + profile]


def main():
    parser = argparse.ArgumentParser(description=__doc__, allow_abbrev=False)
    parser.add_argument("action", choices=["doctor", "run"])
    parser.add_argument("operation", choices=sorted(CONFIG["operations"]))
    args = parser.parse_args(sys.argv[1:3])
    business = sys.argv[3:]
    if args.action == "doctor":
        business = [arg for arg in business if arg != "--json"]
    spec = CONFIG["operations"][args.operation]
    script = SCRIPTS / spec["script"]
    if args.action == "run" and any(v in ("-h", "--help") for v in business):
        return subprocess.call([sys.executable, "-B", str(script), *business])
    if args.operation in {"search-materials", "recommend-materials", "search-papers"}:
        selector = argparse.ArgumentParser(add_help=False, allow_abbrev=False)
        selector.add_argument("--sources", nargs="+", default=[])
        selector.add_argument("--mode", default="academic")
        selection, _ = selector.parse_known_args(business)
        sources = set(selection.sources)
        if not sources and selection.mode in {"general", "news"}:
            sources = {"tavily"}
        credential = {frozenset({"mp"}): "MP_API_KEY", frozenset({"tavily"}): "TAVILY_API_KEY"}.get(frozenset(sources))
        if credential and not os.getenv(credential):
            raise ValueError("Configure " + credential + " for the selected source")
    profile = spec.get("profile")
    if profile == "by-input":
        profile = document_profile(business)
    cache = cache_root()
    device = option(business, "--device") or "cpu"
    env = dict(os.environ, PYTHONDONTWRITEBYTECODE="1", PYTHONUTF8="1")

    def check(repair=False):
        python, missing = environment(profile, device, cache, repair)
        resources, extra = prepare(cache, CONFIG, spec.get("resource"), business, env, repair)
        return python, missing + resources, extra

    python, missing, extra = check()
    if args.action == "doctor":
        print(json.dumps({"status": "missing" if missing else "ready", "missing": missing,
                          "operation": args.operation}, ensure_ascii=False))
        return 2 if missing else 0
    if missing:
        with installation_lock(cache):
            check(repair=True)
            python, missing, extra = check()
            if missing:
                raise RuntimeError("Still missing after setup: " + ", ".join(missing))
    return subprocess.call([str(python), "-B", str(script), *business, *extra], env=env)


if __name__ == "__main__":
    try:
        sys.exit(main())
    except (OSError, ValueError, RuntimeError, subprocess.SubprocessError) as exc:
        result = {"status": "blocked", "reason": str(exc), "retry": sys.argv[1:]}
        print(json.dumps(result, ensure_ascii=False), file=sys.stdout if sys.argv[1:2] == ["doctor"] else sys.stderr)
        sys.exit(3)
