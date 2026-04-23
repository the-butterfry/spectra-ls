<!-- Description: Wiki home page for Spectra L/S operations, architecture, contribution flow, and runbooks. -->
<!-- Version: 2026.04.22.11 -->
<!-- Last updated: 2026-04-22 -->

# Spectra L/S Wiki

Spectra L/S is a tactile analog surface for Home Assistant, with deep audio/lighting workflows and broad mappable control capabilities across the home.

This wiki mirrors curated content from [`docs/wiki/`](https://github.com/the-butterfry/spectra-ls/tree/main/docs/wiki) in the main repository and is optimized for operators/contributors who prefer GitHub-native documentation navigation.

## Start here

- [Welcome, README, and Bug Workflow](Welcome-README-and-Bug-Workflow)
- [Install on Your Own Home Assistant](Install-on-Your-Own-HA)
- [Getting Started](Getting-Started)
- [User Setup, Deploy, and HA Integration](User-Setup-Deploy-and-HA-Integration)
- [System Architecture](System-Architecture)
- [Control Surface Inputs and Expanders](Control-Surface-Inputs-and-Expanders)
- [Control Contracts and Scope Paths](Control-Contracts-and-Scope-Paths)
- [Operations Runbooks](Operations-Runbooks)
- [Discussions and Projects Workflow](Discussions-and-Projects-Workflow)
- [Release and Changelog Process](Release-and-Changelog-Process)
- [Documentation Writing Standard](DOCUMENTATION-WRITING-STANDARD)
- [Wiki Content Scope Policy](Wiki-Content-Scope-Policy)
- [Custom Component Setup Roadmap Stub](Custom-Component-Setup-Roadmap-Stub)

## Documentation quality baseline

Current documentation posture:

What that means in practice:

- clearer action-first instructions,
- explicit expected outcomes,
- concrete troubleshooting paths,
- concise language with strong references.

Writing quality standard:

- [`docs/wiki/DOCUMENTATION-WRITING-STANDARD.md`](https://github.com/the-butterfry/spectra-ls/blob/main/docs/wiki/DOCUMENTATION-WRITING-STANDARD.md)

## Operator quick paths

- New install on your own HA: start with **Install on Your Own Home Assistant**
- Existing install troubleshooting: go to **Operations Runbooks**
- Bug submission and triage flow: use **Welcome, README, and Bug Workflow**
- Process/governance routing: use **Discussions and Projects Workflow**

## Source of truth

- Canonical docs index: [`docs/README.md`](https://github.com/the-butterfry/spectra-ls/blob/main/docs/README.md)
- Canonical changelog: [`docs/CHANGELOG.md`](https://github.com/the-butterfry/spectra-ls/blob/main/docs/CHANGELOG.md)
- Runtime roadmap notes: [`docs/roadmap/v-next-NOTES.md`](https://github.com/the-butterfry/spectra-ls/blob/main/docs/roadmap/v-next-NOTES.md)
- Component roadmap notes: [`docs/roadmap/CUSTOM-COMPONENT-ROADMAP.md`](https://github.com/the-butterfry/spectra-ls/blob/main/docs/roadmap/CUSTOM-COMPONENT-ROADMAP.md)

## How this wiki is published

- Source pages live in: [`docs/wiki/`](https://github.com/the-butterfry/spectra-ls/tree/main/docs/wiki)
- Publish pipeline: [`.github/workflows/wiki-sync.yml`](https://github.com/the-butterfry/spectra-ls/blob/main/.github/workflows/wiki-sync.yml)
- Sync trigger: changes to [`docs/wiki/**`](https://github.com/the-butterfry/spectra-ls/tree/main/docs/wiki) on `main` (or manual workflow dispatch)

## What this wiki is for

- User/operator setup, deployment, integration, and bug workflow guidance.
- High-level architecture and process routing.
- Practical checklists that evolve with the custom-component migration.

For deep internals, use [`docs/architecture`](https://github.com/the-butterfry/spectra-ls/tree/main/docs/architecture), [`docs/roadmap`](https://github.com/the-butterfry/spectra-ls/tree/main/docs/roadmap), and [`docs/program`](https://github.com/the-butterfry/spectra-ls/tree/main/docs/program).
