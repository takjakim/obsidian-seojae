#!/bin/sh
set -eu

TARGET_REPOSITORY="takjakim/obsidian-seojae"
SCRIPT_DIR=$(CDPATH= cd -- "$(dirname -- "$0")" && pwd)
REPOSITORY_ROOT=$(CDPATH= cd -- "$SCRIPT_DIR/.." && pwd)

fail() {
  printf '%s\n' "ERROR: $*" >&2
  exit 1
}

command -v git >/dev/null 2>&1 || fail "git is required"
command -v gh >/dev/null 2>&1 || fail "GitHub CLI (gh) is required"
command -v python3 >/dev/null 2>&1 || fail "python3 is required"

GIT_ROOT=$(git -C "$REPOSITORY_ROOT" rev-parse --show-toplevel 2>/dev/null) || fail "not a Git repository"
[ "$GIT_ROOT" = "$REPOSITORY_ROOT" ] || fail "run this only from the standalone obsidian-seojae repository"
[ "$(git -C "$REPOSITORY_ROOT" branch --show-current)" = "main" ] || fail "current branch must be main"
[ -z "$(git -C "$REPOSITORY_ROOT" status --porcelain)" ] || fail "working tree must be clean"

python3 "$SCRIPT_DIR/validate.py" --root "$REPOSITORY_ROOT"

VERSION=$(python3 -c 'import json,sys; print(json.load(open(sys.argv[1], encoding="utf-8"))["version"])' "$REPOSITORY_ROOT/manifest.json")
[ -f "$REPOSITORY_ROOT/release-notes.md" ] || fail "release-notes.md is required"

gh auth status --hostname github.com >/dev/null 2>&1 || fail "cannot verify GitHub authentication or connectivity for github.com"
AUTHENTICATED_OWNER=$(gh api user --jq .login 2>/dev/null) || fail "cannot reach GitHub or read the authenticated account"
[ "$AUTHENTICATED_OWNER" = "takjakim" ] || fail "gh must be authenticated as takjakim (currently $AUTHENTICATED_OWNER)"

ORIGIN_URL=$(git -C "$REPOSITORY_ROOT" remote get-url origin 2>/dev/null || true)
case "$ORIGIN_URL" in
  ""|"https://github.com/$TARGET_REPOSITORY"|"https://github.com/$TARGET_REPOSITORY.git"|"git@github.com:$TARGET_REPOSITORY.git") ;;
  *) fail "existing origin points somewhere else: $ORIGIN_URL" ;;
esac

REPOSITORY_EXISTS=0
REPOSITORY_JSON=$(gh api "repos/$TARGET_REPOSITORY" 2>&1) && REPOSITORY_EXISTS=1 || {
  case "$REPOSITORY_JSON" in
    *"HTTP 404"*) REPOSITORY_EXISTS=0 ;;
    *) fail "cannot inspect $TARGET_REPOSITORY: $REPOSITORY_JSON" ;;
  esac
}

if [ "$REPOSITORY_EXISTS" -eq 1 ]; then
  REPOSITORY_PRIVATE=$(printf '%s' "$REPOSITORY_JSON" | python3 -c 'import json,sys; print(str(json.load(sys.stdin)["private"]).lower())')
  [ "$REPOSITORY_PRIVATE" = "false" ] || fail "$TARGET_REPOSITORY exists but is private"
fi

LOCAL_HEAD=$(git -C "$REPOSITORY_ROOT" rev-parse HEAD)
REMOTE_MAIN=""
REMOTE_TAG=""
if [ "$REPOSITORY_EXISTS" -eq 1 ]; then
  REMOTE_REFS=$(git ls-remote "https://github.com/$TARGET_REPOSITORY.git") || fail "cannot read refs from $TARGET_REPOSITORY"
  REMOTE_MAIN=$(printf '%s\n' "$REMOTE_REFS" | awk '$2 == "refs/heads/main" { print $1; exit }')
  REMOTE_HEADS=$(printf '%s\n' "$REMOTE_REFS" | awk '$2 ~ /^refs\/heads\// { print $2 }')
  if [ -n "$REMOTE_HEADS" ] && [ -z "$REMOTE_MAIN" ]; then
    fail "$TARGET_REPOSITORY has branches but no main branch; refusing to add unrelated history"
  fi
  REMOTE_TAG=$(printf '%s\n' "$REMOTE_REFS" | awk -v ref="refs/tags/$VERSION^{}" '$2 == ref { print $1; exit }')
  if [ -z "$REMOTE_TAG" ]; then
    REMOTE_TAG=$(printf '%s\n' "$REMOTE_REFS" | awk -v ref="refs/tags/$VERSION" '$2 == ref { print $1; exit }')
  fi
  if [ -n "$REMOTE_TAG" ] && [ "$REMOTE_TAG" != "$LOCAL_HEAD" ]; then
    fail "remote tag $VERSION already points to a different commit"
  fi

  RELEASE_EXISTS=0
  RELEASE_JSON=$(gh api "repos/$TARGET_REPOSITORY/releases/tags/$VERSION" 2>&1) && RELEASE_EXISTS=1 || {
    case "$RELEASE_JSON" in
      *"HTTP 404"*) RELEASE_EXISTS=0 ;;
      *) fail "cannot inspect release $VERSION: $RELEASE_JSON" ;;
    esac
  }
  if [ "$RELEASE_EXISTS" -eq 1 ]; then
    [ -n "$REMOTE_TAG" ] || fail "release $VERSION exists without a matching remote tag"
    RELEASE_METADATA=$(printf '%s' "$RELEASE_JSON" | python3 -c 'import json,sys; r=json.load(sys.stdin); print(r["tag_name"], str(r.get("draft", False)).lower(), str(r.get("prerelease", False)).lower())')
    set -- $RELEASE_METADATA
    RELEASE_TAG=$1
    RELEASE_DRAFT=$2
    RELEASE_PRERELEASE=$3
    [ "$RELEASE_TAG" = "$VERSION" ] || fail "existing release uses an unexpected tag: $RELEASE_TAG"
    [ "$RELEASE_DRAFT" = "false" ] || fail "release $VERSION exists as a draft; publish it explicitly before retrying"
    [ "$RELEASE_PRERELEASE" = "false" ] || fail "release $VERSION exists as a prerelease; a stable theme release is required"
    TEMP_DIR=$(mktemp -d "${TMPDIR:-/tmp}/seojae-release.XXXXXX")
    trap 'rm -rf "$TEMP_DIR"' EXIT HUP INT TERM
    gh release download "$VERSION" --repo "$TARGET_REPOSITORY" --pattern theme.css --pattern manifest.json --dir "$TEMP_DIR" >/dev/null
    cmp -s "$REPOSITORY_ROOT/theme.css" "$TEMP_DIR/theme.css" || fail "existing release theme.css differs from the local artifact"
    cmp -s "$REPOSITORY_ROOT/manifest.json" "$TEMP_DIR/manifest.json" || fail "existing release manifest.json differs from the local artifact"
    printf '%s\n' "Release $VERSION already exists and its artifacts match. Nothing to publish."
    exit 0
  fi
fi

if [ -n "$REMOTE_MAIN" ]; then
  if [ "$ORIGIN_URL" = "" ]; then
    git -C "$REPOSITORY_ROOT" remote add origin "https://github.com/$TARGET_REPOSITORY.git"
    ORIGIN_URL="https://github.com/$TARGET_REPOSITORY.git"
  fi
  git -C "$REPOSITORY_ROOT" fetch --no-tags origin refs/heads/main:refs/remotes/origin/main
  git -C "$REPOSITORY_ROOT" merge-base --is-ancestor refs/remotes/origin/main HEAD || fail "remote main is not an ancestor of local main"
fi

if git -C "$REPOSITORY_ROOT" show-ref --verify --quiet "refs/tags/$VERSION"; then
  [ "$(git -C "$REPOSITORY_ROOT" rev-list -n 1 "$VERSION")" = "$LOCAL_HEAD" ] || fail "local tag $VERSION points to a different commit"
else
  git -C "$REPOSITORY_ROOT" tag -a "$VERSION" -m "Seojae $VERSION"
fi

if [ "$REPOSITORY_EXISTS" -eq 0 ]; then
  if [ "$ORIGIN_URL" = "" ]; then
    gh repo create "$TARGET_REPOSITORY" --public --source "$REPOSITORY_ROOT" --remote origin
    ORIGIN_URL="https://github.com/$TARGET_REPOSITORY.git"
  else
    gh repo create "$TARGET_REPOSITORY" --public
  fi
elif [ "$ORIGIN_URL" = "" ]; then
  git -C "$REPOSITORY_ROOT" remote add origin "https://github.com/$TARGET_REPOSITORY.git"
fi

git -C "$REPOSITORY_ROOT" push origin main
git -C "$REPOSITORY_ROOT" push origin "refs/tags/$VERSION"
gh release create "$VERSION" \
  "$REPOSITORY_ROOT/theme.css" \
  "$REPOSITORY_ROOT/manifest.json" \
  --repo "$TARGET_REPOSITORY" \
  --title "Seojae $VERSION" \
  --notes-file "$REPOSITORY_ROOT/release-notes.md" \
  --verify-tag

TEMP_DIR=$(mktemp -d "${TMPDIR:-/tmp}/seojae-release.XXXXXX")
trap 'rm -rf "$TEMP_DIR"' EXIT HUP INT TERM
gh release download "$VERSION" --repo "$TARGET_REPOSITORY" --pattern theme.css --pattern manifest.json --dir "$TEMP_DIR" >/dev/null
cmp -s "$REPOSITORY_ROOT/theme.css" "$TEMP_DIR/theme.css" || fail "published theme.css verification failed"
cmp -s "$REPOSITORY_ROOT/manifest.json" "$TEMP_DIR/manifest.json" || fail "published manifest.json verification failed"
printf '%s\n' "Published and verified https://github.com/$TARGET_REPOSITORY/releases/tag/$VERSION"
