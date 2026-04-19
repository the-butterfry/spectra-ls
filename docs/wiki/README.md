<!-- Description: Wiki source and synchronization instructions for Spectra documentation pages. -->
<!-- Version: 2026.04.19.1 -->
<!-- Last updated: 2026-04-19 -->

# Wiki Source + Sync

This folder stores wiki-source markdown pages.

## Source pages

- `Home.md` → wiki Home page

## Optional sync automation

Use `bin/sync_docs_to_wiki.sh` to push `docs/wiki/*.md` to your GitHub wiki repository.

Required environment variables:

- `WIKI_REPOSITORY` (format: `owner/repo`)
- `WIKI_PUSH_TOKEN` (GitHub token with wiki write access)

Example (optional):

- `WIKI_REPOSITORY=owner/repo WIKI_PUSH_TOKEN=*** bin/sync_docs_to_wiki.sh`
