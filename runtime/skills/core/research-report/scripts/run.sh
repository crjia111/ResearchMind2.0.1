#!/bin/sh
set -eu
here=$(CDPATH= cd -- "$(dirname -- "$0")" && pwd)
cache=${RM_CACHE_DIR:-${XDG_CACHE_HOME:-$HOME/.cache}/researchmind}
export RM_CACHE_DIR="$cache" PYTHONDONTWRITEBYTECODE=1 PYTHONUTF8=1
uv_bin="$cache/bin/uv-0.13.9"
export UV_CACHE_DIR="${UV_CACHE_DIR:-$cache/uv-cache}" UV_PYTHON_INSTALL_DIR="${UV_PYTHON_INSTALL_DIR:-$cache/python}"
ensure_uv() {
    if command -v uv >/dev/null 2>&1; then command -v uv; return; fi
    if [ -x "$uv_bin" ]; then printf '%s\n' "$uv_bin"; return; fi
    case "$(uname -s)/$(uname -m)" in
        Linux/x86_64) target=x86_64-unknown-linux-gnu; sha=a7fbaff2b9a271d85c1bdb540941090fd1ce011797b4abeb48e4dcd39c2471d5 ;;
        Darwin/arm64) target=aarch64-apple-darwin; sha=5aeca67f2283f75235de40d0bd9c0a5bbc5fce23b6d48b3bf9fa1b2db08382ca ;;
        *) echo "Install uv for this OS/architecture." >&2; return 3 ;;
    esac
    mkdir -p "$cache/bin"
    temp=$(mktemp -d "$cache/bin/uv.XXXXXX")
    trap 'rm -f "$temp/uv.tgz" "$temp/uv"; rmdir "$temp" 2>/dev/null || true' EXIT
    curl -fLsS --retry 2 "https://github.com/astral-sh/uv/releases/download/0.13.9/uv-$target.tar.gz" -o "$temp/uv.tgz"
    if command -v sha256sum >/dev/null; then actual=$(sha256sum "$temp/uv.tgz"); else actual=$(shasum -a 256 "$temp/uv.tgz"); fi
    [ "${actual%% *}" = "$sha" ] || { echo "uv archive checksum mismatch" >&2; exit 3; }
    tar -xzOf "$temp/uv.tgz" "uv-$target/uv" > "$temp/uv"
    chmod 755 "$temp/uv"
    mv -f "$temp/uv" "$uv_bin"
    printf '%s\n' "$uv_bin"
}
if [ "${1:-}" = _ensure_uv ]; then ensure_uv; exit; fi
for py in python3 python; do
    if command -v "$py" >/dev/null && "$py" -c 'import sys; sys.exit(sys.version_info < (3, 11))'; then
        exec "$py" -B "$here/runtime.py" "$@"
    fi
done
existing_uv=$(command -v uv || true)
[ -n "$existing_uv" ] || existing_uv=$uv_bin
if [ -x "$existing_uv" ]; then
    managed=$("$existing_uv" python find --managed-python --no-python-downloads 3.12 2>/dev/null || true)
    if [ -x "$managed" ]; then exec "$managed" -B "$here/runtime.py" "$@"; fi
fi
if [ "${1:-}" = doctor ]; then echo '{"status":"missing","missing":["Python 3.11+; run prepares Python 3.12"]}'; exit 2; fi
uv_path=$(ensure_uv)
exec "$uv_path" run --no-project --managed-python --python 3.12 python -B "$here/runtime.py" "$@"
