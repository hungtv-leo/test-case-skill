#!/usr/bin/env bash
# Install self-test-cases skill into the current project's .cursor/skills/ folder.
# Copies ONLY runtime files listed in install.manifest (no scripts/tests, no .git).
#
# Usage (from target project root):
#   curl -fsSL https://raw.githubusercontent.com/hungtv-leo/test-case-skill/main/install.sh | bash
#
# Local source:
#   ./install.sh --source /path/to/skill-repo --project /path/to/your-app
set -euo pipefail

REPO="${REPO:-hungtv-leo/test-case-skill}"
BRANCH="${BRANCH:-main}"
SKILL_NAME="${SKILL_NAME:-self-test-cases}"
PROJECT_ROOT="${PROJECT_ROOT:-$(pwd)}"
SOURCE=""

while [[ $# -gt 0 ]]; do
  case "$1" in
    --project) PROJECT_ROOT="$2"; shift 2 ;;
    --source) SOURCE="$2"; shift 2 ;;
    --repo) REPO="$2"; shift 2 ;;
    --branch) BRANCH="$2"; shift 2 ;;
    *) echo "Unknown arg: $1" >&2; exit 1 ;;
  esac
done

DEST="$PROJECT_ROOT/.cursor/skills/$SKILL_NAME"
TMP=""

cleanup() {
  if [[ -n "${TMP}" && -d "${TMP}" ]]; then
    rm -rf "${TMP}"
  fi
}
trap cleanup EXIT

read_manifest() {
  # strip comments/blank lines
  sed -e 's/\r$//' -e 's/#.*$//' -e '/^[[:space:]]*$/d' "$1"
}

copy_runtime() {
  local from="$1"
  local to="$2"
  local manifest="$3"
  mkdir -p "$to"
  while IFS= read -r rel; do
    rel="${rel#"${rel%%[![:space:]]*}"}"
    rel="${rel%"${rel##*[![:space:]]}"}"
    [[ -z "$rel" ]] && continue
    local src="$from/$rel"
    if [[ ! -e "$src" ]]; then
      echo "Warning: skip missing file in source: $rel" >&2
      continue
    fi
    local dst="$to/$rel"
    mkdir -p "$(dirname "$dst")"
    cp -f "$src" "$dst"
  done < <(read_manifest "$manifest")
}

if [[ -n "$SOURCE" ]]; then
  FROM="$(cd "$SOURCE" && pwd)"
  MANIFEST="$FROM/install.manifest"
  if [[ ! -f "$MANIFEST" ]]; then
    echo "install.manifest not found in Source: $FROM" >&2
    exit 1
  fi
  echo "Installing from local source: $FROM"
else
  TMP="$(mktemp -d "${TMPDIR:-/tmp}/self-test-cases-install.XXXXXX")"
  ZIP_URL="https://github.com/${REPO}/archive/refs/heads/${BRANCH}.zip"
  echo "Downloading ${ZIP_URL} ..."
  curl -fsSL "$ZIP_URL" -o "$TMP/skill.zip"
  unzip -q "$TMP/skill.zip" -d "$TMP"
  FROM="$(find "$TMP" -mindepth 1 -maxdepth 1 -type d | head -n 1)"
  MANIFEST="$FROM/install.manifest"
  if [[ ! -f "$MANIFEST" ]]; then
    echo "install.manifest missing in downloaded archive (branch=${BRANCH})." >&2
    exit 1
  fi
  echo "Installing from GitHub: ${REPO}@${BRANCH}"
fi

COUNT="$(read_manifest "$MANIFEST" | wc -l | tr -d ' ')"
if [[ "$COUNT" -eq 0 ]]; then
  echo "install.manifest is empty." >&2
  exit 1
fi

if [[ -d "$DEST" ]]; then
  echo "Replacing existing install: $DEST"
  rm -rf "$DEST"
fi

copy_runtime "$FROM" "$DEST" "$MANIFEST"
mkdir -p "$DEST/workdir"

if [[ ! -f "$DEST/SKILL.md" ]]; then
  echo "Install failed: SKILL.md missing at $DEST" >&2
  exit 1
fi

for rel in scripts/tests README.md install.ps1 install.sh install.manifest .gitignore .git; do
  if [[ -e "$DEST/$rel" ]]; then
    echo "Install polluted: unexpected path copied: $rel" >&2
    exit 1
  fi
done

echo
echo "[OK] Installed runtime skill -> $DEST"
echo "     ${COUNT} skill files only (no README/install/tests/.git)"
echo
echo "Next:"
echo "  pip install --user -r \"$DEST/scripts/requirements.txt\""
echo "  Restart Cursor, then run: /self-test-cases"
