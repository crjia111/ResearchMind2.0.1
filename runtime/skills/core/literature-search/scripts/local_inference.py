"""Start the bundled llama.cpp server on a private, temporary loopback port."""

import atexit
from functools import lru_cache
import json
import os
from pathlib import Path
import secrets
import socket
import subprocess
from tempfile import TemporaryFile
import time
import urllib.error
import urllib.request

ROOT = Path(__file__).resolve().parents[1]
SERVER = Path(os.getenv("RM_LLAMA_SERVER") or ROOT / "engine" / ("llama-server.exe" if os.name == "nt" else "llama-server")).resolve()
MODEL_DIR = Path(os.getenv("RM_MODEL_DIR") or ROOT / "models").resolve()
OPENER = urllib.request.build_opener(urllib.request.ProxyHandler({}))


def installed(filename):
    return SERVER.is_file() and (MODEL_DIR / filename).is_file()


class Server:
    def __init__(self, filename, mode):
        token = secrets.token_urlsafe(24)
        with socket.socket() as listener:
            listener.bind(("127.0.0.1", 0))
            port = listener.getsockname()[1]
        self.base = f"http://127.0.0.1:{port}"
        self.headers = {"Authorization": f"Bearer {token}", "Content-Type": "application/json"}
        args = [
            str(SERVER), "--host", "127.0.0.1", "--port", str(port), "--api-key", token,
            "--model", filename, "--alias", "bundled",
            "--threads", str(min(4, os.cpu_count() or 1)), "--n-gpu-layers", "0",
        ]
        if mode == "embedding":
            args += ["--embedding", "--pooling", "last", "--ctx-size", "2048", "--ubatch-size", "2048"]
        else:
            args += ["--ctx-size", "16384"]
        with TemporaryFile() as log:
            self.process = subprocess.Popen(
                args, cwd=MODEL_DIR, stdout=log, stderr=log,
                creationflags=getattr(subprocess, "CREATE_NO_WINDOW", 0),
            )
            try:
                self.wait_ready(log)
            except BaseException:
                self.close()
                raise
        atexit.register(self.close)

    def wait_ready(self, log):
        deadline = time.monotonic() + 90
        while time.monotonic() < deadline:
            if self.process.poll() is not None:
                log.seek(max(0, log.seek(0, os.SEEK_END) - 2048))
                detail = log.read().decode("utf-8", errors="replace")
                raise RuntimeError(f"Bundled inference server exited with {self.process.returncode}: {detail}")
            try:
                req = urllib.request.Request(self.base + "/health", headers=self.headers)
                with OPENER.open(req, timeout=2) as response:
                    if json.load(response).get("status") == "ok":
                        return
            except (OSError, ValueError):
                time.sleep(0.25)
        raise RuntimeError("Bundled inference server did not become ready")

    def request(self, route, payload):
        req = urllib.request.Request(self.base + route, json.dumps(payload).encode("utf-8"),
                                     headers=self.headers)
        try:
            with OPENER.open(req, timeout=300) as response:
                return json.load(response)
        except urllib.error.HTTPError as error:
            raise RuntimeError(f"Bundled inference returned HTTP {error.code}") from None
        except OSError:
            raise RuntimeError("Could not reach bundled inference server") from None

    def close(self):
        if self.process.poll() is None:
            self.process.terminate()
            try:
                self.process.wait(timeout=5)
            except subprocess.TimeoutExpired:
                self.process.kill()
                self.process.wait()


@lru_cache(maxsize=2)
def inference(filename, mode):
    if not installed(filename):
        raise FileNotFoundError(f"Run the skill launcher to prepare the engine and {filename}")
    return Server(filename, mode)
