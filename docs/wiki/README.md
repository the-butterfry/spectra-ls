<!-- Description: Wiki source and synchronization instructions for Spectra documentation pages. -->
<!-- Version: 2026.04.21.9 -->
<!-- Last updated: 2026-04-21 -->

# Wiki Source + Sync

This folder stores the source pages for GitHub Wiki publishing.

## Architecture

- Source of truth: `docs/wiki/*.md`
- Publish target: `<owner>/<repo>.wiki.git`
- Automation: `.github/workflows/wiki-sync.yml`

## Core page inventory

- `Home.md`
- `Welcome-README-and-Bug-Workflow.md`
- `Install-on-Your-Own-HA.md`
- `User-Setup-Deploy-and-HA-Integration.md`
- `Discussions-and-Projects-Workflow.md`
- `Operations-Runbooks.md`
- `Release-and-Changelog-Process.md`
- `Contributing-Workflow.md`
- `System-Architecture.md`
- `Control-Surface-Inputs-and-Expanders.md`
- `Control-Contracts-and-Scope-Paths.md`
- `Wiki-Content-Scope-Policy.md`
- `DOCUMENTATION-WRITING-STANDARD.md`
- `Custom-Component-Setup-Roadmap-Stub.md`

## Content scope policy

Use `Wiki-Content-Scope-Policy.md` to decide what belongs in wiki versus deep docs under `docs/architecture`, `docs/roadmap`, and `docs/program`.

Use `DOCUMENTATION-WRITING-STANDARD.md` to enforce direct, native-English, task-oriented page quality across all wiki pages.

## One-time enablement checklist

1. In the GitHub repository, enable **Settings → General → Features → Wikis**.
2. Open the repo **Wiki** tab and create/save the first `Home` page (initializes `<repo>.wiki.git`).
3. Create a fine-grained PAT with wiki push capability.
4. Add the token as repository secret: `WIKI_FINE_GRAINED_PAT`.
5. Commit wiki pages in `docs/wiki/` to `main`.
6. Confirm workflow run `Wiki Sync` succeeds.

## How to create the fine-grained PAT

1. From your GitHub profile avatar (top-right), go to **Settings → Developer settings → Personal access tokens → Fine-grained tokens**.
   - Direct URL fallback: `https://github.com/settings/personal-access-tokens/new`
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

## Troubleshooting failed `Wiki Sync` runs

- `Node.js 20 actions are deprecated` is a warning, not the root failure by itself.
- `Process completed with exit code 128` in sync steps usually means one of:
   1. Wiki repo not reachable (Wikis disabled or not initialized)
   2. PAT auth failure to `<owner>/<repo>.wiki.git`
   3. PAT scope/repository selection mismatch

Quick checks:

1. Confirm wiki is enabled: **Repo Settings → General → Features → Wikis**
2. Confirm secret exists: `WIKI_FINE_GRAINED_PAT`
3. Confirm PAT has repository **Contents: Read and write** and includes this repo.
4. Re-run `Wiki Sync` from Actions after saving any change under `docs/wiki/`.
