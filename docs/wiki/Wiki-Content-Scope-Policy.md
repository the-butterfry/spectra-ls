<!-- Description: Policy for wiki content boundaries, ownership, and parity with repository docs. -->
<!-- Version: 2026.04.22.2 -->
<!-- Last updated: 2026-04-22 -->

# Wiki Content Scope Policy

This policy keeps wiki content useful, concise, and user-focused.

## What SHOULD be in wiki

- User/operator setup and deployment runbooks
- Home Assistant integration guidance
- Bug submission and support workflow
- High-level architecture navigation pages
- Governance intake flow (Discussions → Issues → Projects → PR)
- Release/changelog orientation pages

## What SHOULD NOT be in wiki

- Deep low-level implementation internals better suited to `docs/architecture/`
- Exhaustive branch-specific engineering notes better suited to `docs/roadmap/`, `docs/program/`, `docs/notes/`
- Temporary scratch investigations without enduring operator value
- Secret values, private topology details, or environment-specific credentials

## Source-of-truth hierarchy

1. Canonical technical detail: `docs/`
2. Canonical user-facing overview: `README.md`
3. Wiki: user/operator-friendly navigation + runbooks synchronized from `docs/wiki/`

## Linked references

- Wiki writing standard: [`docs/wiki/DOCUMENTATION-WRITING-STANDARD.md`](https://github.com/the-butterfry/spectra-ls/blob/main/docs/wiki/DOCUMENTATION-WRITING-STANDARD.md)
- Wiki source index: [`docs/wiki/README.md`](https://github.com/the-butterfry/spectra-ls/blob/main/docs/wiki/README.md)
- Docs index: [`docs/README.md`](https://github.com/the-butterfry/spectra-ls/blob/main/docs/README.md)
- Architecture docs: [`docs/architecture/`](https://github.com/the-butterfry/spectra-ls/tree/main/docs/architecture)
- Roadmaps and planning docs: [`docs/roadmap/`](https://github.com/the-butterfry/spectra-ls/tree/main/docs/roadmap), [`docs/program/`](https://github.com/the-butterfry/spectra-ls/tree/main/docs/program), [`docs/notes/`](https://github.com/the-butterfry/spectra-ls/tree/main/docs/notes)

## Mature-project pattern (recommended)

Mature repositories typically separate concerns:

- user and operator guidance in wiki/docs portals,
- contributor engineering details in contributor/governance docs,
- deep internals in architecture and roadmap docs.

Spectra follows that same split to keep onboarding simple while preserving technical rigor.
