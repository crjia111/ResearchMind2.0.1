"""Verified upstream downloads and local model paths for one installed skill."""
import hashlib
import json
import os
from pathlib import Path
import platform
import sysconfig
import shutil
import stat
import sys
import tarfile
from tempfile import TemporaryDirectory
import urllib.request
import zipfile


def architecture():
    return (platform.machine() or sysconfig.get_platform().removeprefix("win-")).lower()


def digest(path):
    with path.open("rb") as stream:
        return hashlib.file_digest(stream, "sha256").hexdigest()


def fetch(spec, dest):
    source = os.getenv("RM_ASSET_DIR")
    if source and (Path(source) / spec["archive"]).is_file():
        shutil.copyfile(Path(source) / spec["archive"], dest)
    else:
        print("Downloading " + spec["archive"], file=sys.stderr, flush=True)
        with urllib.request.urlopen(spec["url"], timeout=120) as reply, dest.open("wb") as out:
            shutil.copyfileobj(reply, out)
    if digest(dest) != spec["sha256"]:
        raise ValueError("SHA-256 mismatch for " + spec["archive"])


def option(args, name):
    for pos, value in enumerate(args):
        if value == name and pos + 1 < len(args):
            return args[pos + 1]
        if value.startswith(name + "="):
            return value.split("=", 1)[1]
    return None


def install_file(spec, target, repair):
    expected = spec.get("member_sha256", spec["sha256"])
    if target.is_file() and digest(target) == expected:
        return True
    if not repair:
        return False
    target.parent.mkdir(parents=True, exist_ok=True)
    with TemporaryDirectory(dir=target.parent) as scratch:
        path = Path(scratch) / "download"
        fetch(spec, path)
        if spec.get("member"):
            with tarfile.open(path) as archive:
                entry = archive.getmember(spec["member"])
                if not entry.isfile():
                    raise ValueError("Checkpoint must be a regular file")
                result = Path(scratch) / "checkpoint"
                with archive.extractfile(entry) as src, result.open("wb") as dst:
                    shutil.copyfileobj(src, dst)
            if digest(result) != expected:
                raise ValueError("Checkpoint hash mismatch")
            path = result
        path.replace(target)
    return True


def engine(cache, configs, repair):
    custom = os.getenv("RM_LLAMA_SERVER")
    if custom:
        path = Path(custom).resolve()
        return path if path.is_file() and os.access(path, os.X_OK) else None
    key = platform.system() + "-" + architecture()
    if key not in configs:
        raise ValueError("Supply RM_LLAMA_SERVER for " + key)
    spec = configs[key]
    root = cache / "engine" / spec["sha256"]
    state = root / "installed.json"
    if state.is_file():
        try:
            data = json.loads(state.read_text(encoding="utf8"))
            files = data["files"]
            if (data["server"] in files and all(Path(name).name == name and
                    (root / name).is_file() and digest(root / name) == sha for name, sha in files.items())):
                return root / data["server"]
        except (ValueError, KeyError, AttributeError, TypeError):
            pass  # A partial cache record can be rebuilt from the verified upstream archive.
    if not repair:
        return None
    root.mkdir(parents=True, exist_ok=True)
    with TemporaryDirectory(dir=root) as scratch:
        stage = Path(scratch)
        archive = stage / "download.zip"
        fetch(spec, archive)
        names = {}
        with zipfile.ZipFile(archive) as z:
            members = {i.filename: i for i in z.infolist() if not i.is_dir()}
            server, = [n for n in members if Path(n).name in ("llama-server", "llama-server.exe")]
            for name, entry in members.items():
                base = Path(name).name
                if base != Path(server).name and not (base.endswith((".dll", ".dylib")) or ".so" in base):
                    continue
                if base in names:
                    raise ValueError("Duplicate library in engine archive")
                seen = set()
                while stat.S_ISLNK(entry.external_attr >> 16):
                    if entry.filename in seen:
                        raise ValueError("Cyclic engine library link")
                    seen.add(entry.filename)
                    destination = z.read(entry).decode()
                    if Path(destination).name != destination:
                        raise ValueError("Invalid library link")
                    entry = members[(Path(entry.filename).parent / destination).as_posix()]
                temp = stage / base
                with z.open(entry) as src, temp.open("wb") as out:
                    shutil.copyfileobj(src, out)
                temp.chmod(0o755)
                names[base] = digest(temp)
                temp.replace(root / base)
        record = stage / "state"
        record.write_text(json.dumps({"server": Path(server).name, "files": names}), encoding="utf8")
        record.replace(state)
    return root / Path(server).name


def prepare(cache, config, kind, args, env, repair):
    """Return missing resources and additional CLI options without changing user paths."""
    if not kind:
        return [], []
    if kind in ("chat", "embedding"):
        backend = "RM_CHAT_BACKEND" if kind == "chat" else "RM_EMBED_BACKEND"
        if env.get(backend, "local") == "remote":
            valid = env.get("OPENAI_API_KEY") if kind == "chat" else (
                env.get("GOOGLE_API_KEY") or env.get("OPENAI_API_KEY") and env.get("OPENAI_EMBEDDING_MODEL"))
            if not valid:
                raise ValueError("Configure credentials for explicitly selected " + backend + "=remote")
            return [], []
    specs = config["assets"][kind]
    target_dir = cache / "models" / kind
    custom_dir = option(args, "--model-dir")
    custom_file = option(args, "--model-path")
    missing = []
    for spec in specs:
        target = Path(custom_dir or target_dir) / spec["name"]
        override = custom_file or (option(args, "--atom-init") if spec["name"] == "atom_init.json" else None)
        if override:
            target = Path(override)
        if custom_dir or override:
            if not target.is_file():
                raise ValueError("User-specified asset missing: " + str(target))
            continue
        if not install_file(spec, target, repair):
            missing.append(str(target))
    if kind in ("chat", "embedding"):
        server = engine(cache, config["engines"], repair)
        if server:
            env.update(RM_LLAMA_SERVER=str(server), RM_MODEL_DIR=str(target_dir))
        else:
            missing.append("llama-server")
        return missing, []
    if kind == "matter":
        extra = [] if custom_file else ["--model-path", str(target_dir / specs[0]["name"])]
    else:
        extra = [] if custom_dir else ["--model-dir", str(target_dir)]
    return missing, extra
