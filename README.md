# Sonoff Dongle-M OpenThread Border Router

An upstream-based OpenThread Border Router firmware for the Sonoff Dongle-M.
The original Dongle-M proof of concept has been substantially modernised and
rebuilt on top of Espressif's current
[esp-thread-br](https://github.com/espressif/esp-thread-br) architecture.

The ESP32 host runs the Border Router and the onboard EFR32MG24 runs the stock
Sonoff Thread Radio Co-Processor (RCP). The result is a maintainable Dongle-M
implementation with Ethernet, Wi-Fi provisioning/fallback, the standard
Espressif Web UI, and Home Assistant integration.

## What has changed

This is intended as a maintainable successor to the old experimental port:

- rebuilt from current Espressif upstream rather than carrying a heavily modified legacy fork;
- Dongle-M hardware support moved into board/profile and configuration areas;
- hardware GPIO, Ethernet, UART, LED, and connectivity policy isolated from generic Espressif code;
- the standard upstream Web UI retained;
- updated and validated with ESP-IDF v5.5.4;
- deterministic Ethernet-first startup with native Wi-Fi fallback and provisioning;
- controlled infrastructure recovery that preserves Thread state across reboot;
- correct active-high PWM RGB status indication;
- stock onboard MG24 RCP support.

Keeping upstream as the baseline makes future rebases and upstream fixes much
easier to adopt.

## Features

- OpenThread Border Router on the ESP32 host.
- Stock EFR32MG24 Spinel RCP over UART.
- IP101GA Ethernet with Ethernet-first selection.
- Saved Wi-Fi fallback, first-time SoftAP provisioning, and bounded recovery SoftAP.
- Current Espressif/OpenThread Web UI.
- Persistent Thread dataset and network state.
- Home Assistant OpenThread Border Router and Thread integration support.
- One merged ESP32 release image for simple flashing.

## Hardware

The validated hardware is an ESP32-D0WDQ2-V3 host with 16 MB flash and the
onboard EFR32MG24 RCP:

| Function | Dongle-M connection |
| --- | --- |
| RCP UART | UART1, 115200 8N1, no flow control |
| Host UART | RX GPIO13, TX GPIO17 |
| Ethernet PHY | IP101GA, RMII, address 1 |
| Ethernet management | MDC GPIO23, MDIO GPIO18, reset GPIO5, clock GPIO0 |
| RGB LED | Red GPIO4, green GPIO14, blue GPIO2 |

GPIO12 and GPIO15 are defined for MG24 reset and control/hold functions. The
current firmware does not automatically flash or update the MG24.

## Network behaviour

At boot, Ethernet is preferred. If it does not obtain usable connectivity, the
firmware tries saved Wi-Fi credentials. With no saved credentials it starts the
upstream provisioning SoftAP. Repeated saved-Wi-Fi failures lead to a bounded
recovery SoftAP, after which normal connection attempts resume if no new
credentials are supplied.

If Ethernet is lost while Wi-Fi is available, the Dongle-M performs a
controlled reboot so the normal Ethernet-first policy can select Wi-Fi safely.
When Wi-Fi is active, Ethernet must remain stable for 30 seconds before a
controlled reboot returns to preferred Ethernet. This avoids unsafe live
OpenThread backbone rebinding, which the current Espressif integration does not
support atomically.

## LED status

| State | Indication |
| --- | --- |
| Boot | Red → green → blue self-test |
| Ethernet | Blue |
| Wi-Fi | Orange |
| Provisioning/recovery SoftAP | Purple |
| Thread attached | Green pulse, about 200 ms every 2 s |
| Thread detached/disabled | Red pulse, about 200 ms every 2 s, suppressed for about 15 s after Thread startup |

## Installation

Download the merged `sonoff-dongle-m-otbr.bin` and its `.sha256` checksum from
GitHub Releases. Connect the Dongle-M's ESP32 USB interface, identify its serial
port, and flash the image at address `0x0`.

Windows PowerShell:

```powershell
py -m esptool --chip esp32 --port COM3 --baud 460800 --before default_reset --after hard_reset write_flash 0x0 sonoff-dongle-m-otbr.bin
```

Linux/macOS:

```bash
python3 -m esptool --chip esp32 --port /dev/ttyUSB0 --baud 460800 --before default_reset --after hard_reset write_flash 0x0 sonoff-dongle-m-otbr.bin
```

The merged image contains the ESP32 host firmware only. It does not overwrite
or update the onboard MG24 RCP. After flashing, connect Ethernet or use the
provisioning network described below.

### Developer / manual flashing

For source builds, use the exact generated `flash_args` for that build. The
validated host layout is:

```text
0x1000  bootloader/bootloader.bin
0x8000  partition_table/partition-table.bin
0xf000  ota_data_initial.bin
0x20000 esp_ot_br.bin
0x620000 web_storage.bin
```

Do not substitute this layout for another configuration. The generated metadata
is the source of truth.

## First boot and provisioning

- Ethernet connected: the device selects Ethernet and shows blue.
- Saved Wi-Fi available: Wi-Fi is selected if Ethernet is unavailable and shows orange.
- No saved Wi-Fi: the upstream SoftAP starts for provisioning and shows purple.
- Repeated Wi-Fi failure: bounded recovery SoftAP starts; if no replacement credentials are entered, the device retries normal startup.

## Web UI and Thread setup

Open the device IP address in a browser. Use the upstream Espressif/OpenThread
Web UI to inspect the device and form or join a Thread network using the
controls exposed by that release. The selected dataset and Thread state persist
across normal reboots and infrastructure recovery.

## Home Assistant

1. Add the OpenThread Border Router integration using `http://<dongle-ip-address>`.
2. Add the Thread integration.
3. Select the Dongle-M as the preferred Thread network when appropriate.

## Building from source

Use ESP-IDF v5.5.4 and the Dongle-M defaults:

```bash
cd examples/basic_thread_border_router
idf.py -B build-sonoff-dongle-m \
  -D SDKCONFIG=sdkconfig.sonoff_dongle_m \
  -D SDKCONFIG_DEFAULTS=sdkconfig.defaults.sonoff_dongle_m \
  build
```

Generate the merged release image from the resulting ESP-IDF metadata:

```bash
python3 ../../tools/release/merge_dongle_m_image.py \
  examples/basic_thread_border_router/build-sonoff-dongle-m \
  --output artifacts/sonoff-dongle-m-otbr.bin
```

This produces the merged image and `sonoff-dongle-m-otbr.bin.sha256`. The
script consumes `flasher_args.json`, uses its flash map and DIO/40 MHz/16 MB
settings, and packages only the ESP32 host images.

## MG24 RCP status and future work

The supported RCP is the stock Sonoff MG24 OpenThread RCP. A custom reproducible
or bundled RCP is future work; the eventual goal is a reproducible host-plus-RCP
release package without changing the current safe flashing path.

## Recovery / returning to stock

To return to Sonoff firmware, use the official [Sonoff Dongle
Flasher](https://dongle.sonoff.tech/sonoff-dongle-flasher/) and follow Sonoff's
instructions. The merged image is a raw ESP32 flash image and is not intended
for the Sonoff Web UI firmware-update page.

## Credits and upstream

This project builds on Espressif's `esp-thread-br` and ESP-IDF, and on Sonoff's
Dongle-M hardware and stock RCP firmware. See
[docs/sonoff-dongle-m-migration.md](docs/sonoff-dongle-m-migration.md) for
upstream revisions, build evidence, hardware validation, and deferred work.
