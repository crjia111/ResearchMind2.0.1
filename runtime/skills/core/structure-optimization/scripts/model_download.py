"""Install verified scientific model assets into an explicit local directory."""
import argparse
import hashlib
from pathlib import Path
import shutil
import tarfile
from tempfile import TemporaryDirectory
from urllib.request import urlopen

def digest(path):
    with path.open("rb") as stream:
        return hashlib.file_digest(stream, "sha256").hexdigest()


def install_asset(target, url, checksum, offline=None, member=None, extracted_hash=None):
    final_hash = extracted_hash or checksum
    if target.is_file() and digest(target) == final_hash:
        return str(target.resolve())
    filename = url.rsplit("/", 1)[-1]
    from urllib.parse import unquote
    filename = unquote(filename)
    target.parent.mkdir(parents=True, exist_ok=True)
    with TemporaryDirectory(dir=target.parent) as temporary:
        staged = Path(temporary) / filename
        if offline:
            shutil.copyfile(offline / filename, staged)
        else:
            with urlopen(url, timeout=180) as response, staged.open("wb") as stream:
                shutil.copyfileobj(response, stream)
        if digest(staged) != checksum:
            raise ValueError(f"Unexpected SHA-256 for {filename}")
        if member:
            with tarfile.open(staged, "r:gz") as bundle:
                entry = bundle.getmember(member)
                if not entry.isfile():
                    raise ValueError("Expected a regular checkpoint archive member")
                staged = Path(temporary) / target.name
                with bundle.extractfile(entry) as source, staged.open("wb") as destination:
                    shutil.copyfileobj(source, destination)
            if digest(staged) != final_hash:
                raise ValueError(f"Unexpected SHA-256 for {member}")
        staged.replace(target)
    return str(target.resolve())


def cli(assets):
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--model-dir", type=Path, required=True)
    parser.add_argument("--asset-dir", type=Path, help="Use existing downloaded assets")
    args = parser.parse_args()
    paths = [install_asset(args.model_dir / filename, url, checksum, args.asset_dir, *archive)
             for filename, url, checksum, *archive in assets]
    return {"status": "completed", "files": paths}
