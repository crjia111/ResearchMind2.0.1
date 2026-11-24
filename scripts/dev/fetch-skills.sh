#!/usr/bin/env bash
# Fetch optional external skill packs into runtime/skills/external/.
# Runs locally and in CI so the skills never live in this repo's git history.
set -euo pipefail

ROOT="$(cd "$(dirname "$0")/../.." && pwd)"

# ---- Anthropic document skills: docx / pdf / pptx / xlsx ----
# From the Apache-2.0 licensed anthropics/skills repo (each skill directory
# carries its own LICENSE.txt, kept by the copy below).
ANTHROPIC_SKILLS_COMMIT="${ANTHROPIC_SKILLS_COMMIT:-9d2f1ae187231d8199c64b5b762e1bdf2244733d}"
OFFICE_SKILLS="docx pdf pptx xlsx"
OFFICE_OUT="$ROOT/runtime/skills/external/anthropic-skills"

URL="https://github.com/anthropics/skills/archive/${ANTHROPIC_SKILLS_COMMIT}.tar.gz"
TMP="$(mktemp -d)"
echo "Downloading $URL"
curl -fsSL "$URL" -o "$TMP/skills.tar.gz"
tar -xzf "$TMP/skills.tar.gz" -C "$TMP"

SRC="$(find "$TMP" -maxdepth 1 -type d -name 'skills-*' | head -1)"
rm -rf "$OFFICE_OUT"
mkdir -p "$OFFICE_OUT"
for s in $OFFICE_SKILLS; do
  [ -f "$SRC/skills/$s/SKILL.md" ] || { echo "No skills/$s/SKILL.md in archive" >&2; exit 1; }
  cp -R "$SRC/skills/$s" "$OFFICE_OUT/$s"
done
echo "$ANTHROPIC_SKILLS_COMMIT" > "$OFFICE_OUT/.commit"
rm -rf "$TMP"

echo "Placed anthropic-skills@${ANTHROPIC_SKILLS_COMMIT:0:7} in $OFFICE_OUT:"
ls "$OFFICE_OUT"
