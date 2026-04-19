#!/usr/bin/env bash
# Description: Sync docs/wiki pages to GitHub wiki repository using a personal access token.
# Version: 2026.04.19.2
# Last updated: 2026-04-19

set -euo pipefail

wiki_token="${WIKI_PUSH_TOKEN:-${WIKI_FINE_GRAINED_PAT:-}}"

if [[ -z "${wiki_token}" ]]; then
  echo "WIKI_PUSH_TOKEN or WIKI_FINE_GRAINED_PAT is required"
  exit 1
fi

if [[ -z "${WIKI_REPOSITORY:-}" ]]; then
  echo "WIKI_REPOSITORY is required (format: owner/repo)"
  exit 1
fi

repo_root="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
wiki_url="https://x-access-token:${wiki_token}@github.com/${WIKI_REPOSITORY}.wiki.git"
workdir="${repo_root}/.tmp/wiki-sync"

rm -rf "${workdir}"
mkdir -p "${workdir}"

git clone "${wiki_url}" "${workdir}/wiki-repo"
cp -f "${repo_root}"/docs/wiki/*.md "${workdir}/wiki-repo/"

pushd "${workdir}/wiki-repo" >/dev/null
  git config user.name "spectra-docs-bot"
  git config user.email "spectra-docs-bot@users.noreply.github.com"
  git add .
  if git diff --cached --quiet; then
    echo "No wiki changes to push"
    exit 0
  fi
  git commit -m "docs(wiki): sync from docs/wiki"
  git push
popd >/dev/null

echo "Wiki sync complete"
