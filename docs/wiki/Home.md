<!-- Description: Wiki home page for Spectra L/S operations, architecture, contribution flow, and runbooks. -->
<!-- Version: 2026.04.19.2 -->
<!-- Last updated: 2026-04-19 -->

# Spectra L/S Wiki

Spectra L/S is a tactile analog surface for Home Assistant, with deep audio/lighting workflows and broad mappable control capabilities across the home.

This wiki mirrors curated content from `docs/wiki/` in the main repository and is optimized for operators/contributors who prefer GitHub-native documentation navigation.

## Start here

- [Getting Started](Getting-Started)
- [System Architecture](System-Architecture)
- [Control Contracts and Scope Paths](Control-Contracts-and-Scope-Paths)
- [Operations Runbooks](Operations-Runbooks)
- [Discussions and Projects Workflow](Discussions-and-Projects-Workflow)
- [Release and Changelog Process](Release-and-Changelog-Process)

## Source of truth

- Canonical docs index: `docs/README.md`
- Canonical changelog: `docs/CHANGELOG.md`
- Runtime roadmap notes: `docs/roadmap/v-next-NOTES.md`

## How this wiki is published

- Source pages live in: `docs/wiki/`
- Publish pipeline: `.github/workflows/wiki-sync.yml`
- Sync trigger: changes to `docs/wiki/**` on `main` (or manual workflow dispatch)
