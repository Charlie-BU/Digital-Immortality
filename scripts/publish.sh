#!/bin/bash
set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"
ROOT_DIR="$(cd "$SCRIPT_DIR/.." && pwd)"
cd "$ROOT_DIR"

if [ $# -ne 1 ]; then
  echo "Usage: ./scripts/publish.sh <version>"
  echo "Example:"
  echo "  ./scripts/publish.sh 1.2.3"
  echo "  ./scripts/publish.sh v1.2.3"
  exit 1
fi

INPUT_VERSION="$1"
if [[ "$INPUT_VERSION" == v* ]]; then
  TAG="$INPUT_VERSION"
  VERSION="${INPUT_VERSION#v}"
else
  TAG="v$INPUT_VERSION"
  VERSION="$INPUT_VERSION"
fi

if ! [[ "$VERSION" =~ ^[0-9]+\.[0-9]+\.[0-9]+$ ]]; then
  echo "Invalid version: $VERSION (expected format: X.Y.Z)"
  exit 1
fi

echo "Preparing release with version: $VERSION, tag: $TAG"

CURRENT_BRANCH="$(git rev-parse --abbrev-ref HEAD)"
if [ "$CURRENT_BRANCH" != "main" ]; then
  echo "Switching branch: $CURRENT_BRANCH -> main"
  git switch main
fi

echo "Pulling latest main from origin..."
git pull --ff-only origin main

if ! git diff --quiet || ! git diff --cached --quiet; then
  echo "Working tree is not clean. Please commit or stash changes before publishing."
  exit 1
fi

if git rev-parse -q --verify "refs/tags/$TAG" >/dev/null; then
  echo "Tag already exists locally: $TAG"
  exit 1
fi

echo "Updating pyproject.toml version to $VERSION..."
python3 - "$VERSION" <<'PY'
import re
import sys

version = sys.argv[1]
path = "pyproject.toml"
with open(path, "r", encoding="utf-8") as f:
    content = f.read()

updated, count = re.subn(
    r'(?m)^version\s*=\s*"[^"]+"$',
    f'version = "{version}"',
    content,
    count=1,
)
if count != 1:
    raise SystemExit("Failed to update version in pyproject.toml")

with open(path, "w", encoding="utf-8") as f:
    f.write(updated)
PY

echo "Committing version bump..."
git add pyproject.toml
git commit -m "chore(release): $TAG"

echo "Cleaning previous build artifacts..."
rm -rf dist

echo "Building package with uv..."
uv build

echo "Validating distributions with twine..."
uvx twine check dist/*

echo "Creating tag: $TAG"
git tag "$TAG"

echo "Pushing main branch..."
git push origin main

echo "Pushing tag to origin: $TAG"
git push origin "$TAG"

echo "Done. GitHub Actions should now trigger the PyPI publish workflow."
