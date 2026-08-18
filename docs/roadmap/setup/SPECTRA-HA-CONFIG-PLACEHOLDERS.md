<!-- Description: Placeholder snippets for integrating Spectra LS into an existing Home Assistant configuration.yaml. -->
<!-- Version: 2026.05.05.2 -->
<!-- Last updated: 2026-05-05 -->

# Spectra LS Home Assistant Config Placeholders

Use this file as a copy/paste reference for adding Spectra LS requirements into your **existing** `configuration.yaml`.

Do **not** replace your full configuration file with this content.

## Required block

Add (or merge) this under your existing `homeassistant:` section:

```yaml
homeassistant:
  packages: !include_dir_named packages
```

## Optional placeholders

Some Spectra package sets may expect these integrations to be present. If your Home Assistant setup already defines them, keep your existing definitions.

```yaml
template:

command_line:
```

## Deploy verification (LC6-L05 backend/API read lanes)

After deploy/reload, verify component-first backend/API endpoint surfaces are healthy:

- primary: `sensor.component_backend_profile`, `sensor.component_ma_api_url`
- bounded fallback: `sensor.ma_server_profile_effective`, `sensor.ma_api_url`

Expected posture:

- runtime/read consumers prefer component surfaces,
- helper-backed surfaces remain available as rollback-safe compatibility fallback.

## Typical existing includes (for reference only)

Keep your existing include structure; shown here only as examples.

```yaml
# default_config:
# automation: !include automations.yaml
# script: !include scripts.yaml
# scene: !include scenes.yaml
```
