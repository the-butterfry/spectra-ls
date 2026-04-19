<!-- Description: Wiki source and synchronization instructions for Spectra documentation pages. -->
<!-- Version: 2026.04.19.2 -->
<!-- Last updated: 2026-04-19 -->

# Wiki Source + Sync

This folder stores the source pages for GitHub Wiki publishing.

## Architecture

- Source of truth: `docs/wiki/*.md`
- Publish target: `<owner>/<repo>.wiki.git`
- Automation: `.github/workflows/wiki-sync.yml`

## One-time enablement checklist

1. In the GitHub repository, enable **Settings → General → Features → Wikis**.
2. Create a fine-grained PAT with wiki push capability.
3. Add the token as repository secret: `WIKI_FINE_GRAINED_PAT`.
4. Commit wiki pages in `docs/wiki/` to `main`.
5. Confirm workflow run `Wiki Sync` succeeds.

## How to create the fine-grained PAT

1. Go to **GitHub → Settings → Developer settings → Personal access tokens → Fine-grained tokens**.
2. Click **Generate new token**.
3. Token name: `spectra-wiki-sync` (or your preferred name).
4. Resource owner: your user/org that owns this repository.
5. Repository access: **Only select repositories** → select this repository.
6. Permissions:
   - Repository permissions → **Contents: Read and write**
   - Metadata remains read-only by default.
7. Set expiration according to your policy (recommended: short-lived with periodic rotation).
8. Create token and copy it immediately.
9. In repository settings, add secret:
   - Name: `WIKI_FINE_GRAINED_PAT`
   - Value: `<paste token>`

If your org policy blocks fine-grained wiki push, use a classic PAT with `repo` scope as a temporary fallback and store it in the same secret name.

## Manual sync fallback (optional)

You can still run:

- `WIKI_REPOSITORY=owner/repo WIKI_PUSH_TOKEN=*** bin/sync_docs_to_wiki.sh`

This is useful for local dry-runs or emergency publishing when Actions is unavailable.
