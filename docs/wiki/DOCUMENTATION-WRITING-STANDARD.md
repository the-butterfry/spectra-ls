<!-- Description: Writing standard for Spectra documentation and wiki pages, focused on native-English clarity and task completion. -->
<!-- Version: 2026.04.21.1 -->
<!-- Last updated: 2026-04-21 -->

# Documentation Writing Standard (Native-English, Directive, Useful)

Use this standard for `README`, `docs/`, and all `docs/wiki/` pages.

## Why this exists

Some pages currently read like generated text: generic wording, weak action verbs, and low task value.

This standard shifts docs to:

- plain, direct English,
- concrete operator actions,
- clear expected outcomes,
- practical troubleshooting and decision flow.

## Core writing rules

1. **Say what to do, not what might be done**
   - Prefer: “Run X, then verify Y.”
   - Avoid: “X can be used to potentially help with Y.”

2. **Lead with outcome**
   - First 3-5 lines should answer: “What problem does this page solve?”

3. **Use explicit step sequences**
   - Numbered steps for procedures.
   - Include pass/fail checks after each critical stage.

4. **Name real artifacts and surfaces**
   - Include exact file paths, service names, entity names, and menu paths.

5. **Replace vague adjectives with verifiable conditions**
   - Avoid: “works correctly”, “healthy”, “properly configured”.
   - Use: “build completes”, “OTA successful”, “entity state changes within expected interval”.

6. **State boundaries and non-goals explicitly**
   - Include short “In scope / Out of scope” blocks for operational pages.

7. **Troubleshooting must be decisive**
   - Symptom → likely cause → exact action.
   - No hand-wavy “check logs” without where/how/what to look for.

8. **Keep tone human and confident**
   - Short sentences.
   - Active voice.
   - No “AI voice” filler.

## Required page pattern (wiki)

Each operator-facing page should follow this structure:

1. **What this page is for** (2-4 lines)
2. **Before you start** (prerequisites)
3. **Do this** (numbered steps)
4. **Expected result** (pass criteria)
5. **If it fails** (troubleshooting table)
6. **Escalation path** (issue/discussion links)
7. **Source-of-truth references** (canonical docs)

## Anti-patterns to remove during rewrite

- Generic orientation paragraphs with no action.
- Duplicate wording across multiple pages.
- Long roadmap prose inside operator runbooks.
- Ambiguous terms (“soon”, “future”, “maybe”, “generally”).
- Mixed audience pages (operator + deep developer internals in one page).

## Example rewrites

### Weak example A

“This page provides guidance for setup and integration and may evolve over time.”

### Strong example A

“Use this page to install Spectra on your Home Assistant instance and verify audio + lighting control in under 30 minutes.”

---

### Weak example B

“If something is wrong, check your configuration and logs.”

### Strong example B

“If room/target menus are empty after restart: confirm placeholder values are resolved in `docs/setup/SPECTRA-HA-CONFIG-PLACEHOLDERS.md`, then revalidate HA config and refresh helper states.”

## Definition of done for documentation slices

A docs slice is complete only when:

- page language is direct and actionable,
- each procedure includes explicit expected outcomes,
- troubleshooting paths are concrete,
- wiki navigation points users to the right page in 1-2 clicks,
- roadmap/changelog parity entries are updated.
