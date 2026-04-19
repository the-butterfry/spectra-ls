<!-- Description: Policy for wiki content boundaries, ownership, and parity with repository docs. -->
<!-- Version: 2026.04.19.1 -->
<!-- Last updated: 2026-04-19 -->

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

## Mature-project pattern (recommended)

Mature repositories typically separate concerns:

- user and operator guidance in wiki/docs portals,
- contributor engineering details in contributor/governance docs,
- deep internals in architecture and roadmap docs.

Spectra follows that same split to keep onboarding simple while preserving technical rigor.
