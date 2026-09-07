# AGENTS.md

## Project

This repository maintains Sonoff Dongle-M support on top of Espressif's `esp-thread-br`.

Upstream:

```text
https://github.com/espressif/esp-thread-br
```

The goal is to keep the Dongle-M-specific patchset small, isolated and practical to rebase onto current upstream releases.

## Maintenance principles

- Preserve upstream Espressif behaviour wherever practical.
- Keep Dongle-M-specific hardware and product behaviour behind its board profile or dedicated components.
- Do not modify generic upstream behaviour unless genuinely necessary.
- Do not restore the legacy custom Web UI; the current upstream Web UI is authoritative.
- The stock Sonoff EFR32MG24 Thread RCP is the current supported radio firmware.
- Do not enable automatic MG24/RCP flashing without explicit instruction and hardware validation.
- Do not include an RCP image in the ESP32 merged release image.

## Toolchain

The most recently hardware-validated toolchain is:

```text
ESP-IDF v5.5.4
```

Treat this as the known-good baseline, not a permanent version requirement.

When rebasing onto newer Espressif upstream changes:

- use the ESP-IDF version required or recommended by that upstream revision;
- do not downgrade or hold back upstream solely to preserve the previous validated version;
- build and report the exact ESP-IDF version used;
- treat any toolchain change as requiring normal hardware validation before release.

## Dongle-M build

From `examples/basic_thread_border_router`:

```sh
idf.py -B build-sonoff-dongle-m \
  -D SDKCONFIG=sdkconfig.sonoff_dongle_m \
  -D SDKCONFIG_DEFAULTS=sdkconfig.defaults.sonoff_dongle_m \
  build
```

A successful build is not hardware validation.

## Release image

From the repository root:

```sh
python3 tools/release/merge_dongle_m_image.py \
  examples/basic_thread_border_router/build-sonoff-dongle-m \
  --output artifacts/sonoff-dongle-m-otbr.bin
```

The generated merged ESP32 image is flashed at offset `0x0`.

The merge tool must continue to use ESP-IDF-generated flash metadata and must not include MG24/RCP firmware.

## Upstream update workflow

For an upstream refresh:

1. Fetch the latest `upstream/main`.
2. Rebase the Dongle-M work onto it.
3. Resolve only necessary conflicts.
4. Review the resulting Dongle-M-specific delta.
5. Build the Dongle-M firmware.
6. Generate the merged ESP32 image.
7. Report the resulting build status and SHA-256.
8. **STOP.**

Do not claim hardware validation.

Do not publish a release solely because the build succeeds.

## Hardware-validation gate

After a new firmware image is generated, the user performs the physical Dongle-M test.

Only after the user explicitly reports a **HARDWARE PASS** may the validated revision be promoted or published.

If the user reports a failure:

- do not publish;
- record the failure accurately;
- investigate from the tested source/image;
- generate a new candidate;
- return to the hardware-validation gate.

## Publishing

Do not push, tag, create a release, or otherwise promote a newly generated firmware candidate unless the requested workflow explicitly permits it and the required hardware-validation gate has passed.

Generated binaries belong in `artifacts/` or GitHub Release assets and must not be committed to the repository.

## Documentation

Keep:

- `README.md` focused on users, installation and building;
- `docs/sonoff-dongle-m-migration.md` as the concise technical architecture/migration record;
- this file focused only on repository maintenance instructions.

Do not turn documentation into a chronological debugging log.

When changing behaviour, update documentation only after the implementation and its validation status are known.