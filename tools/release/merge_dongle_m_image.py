#!/usr/bin/env python3
"""Build one flash-at-0x0 Dongle-M ESP32 image from ESP-IDF metadata."""

import argparse
import hashlib
import json
import subprocess
import sys
from pathlib import Path


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("build_dir", type=Path, help="ESP-IDF build directory containing flasher_args.json")
    parser.add_argument("--output", type=Path, help="merged output path (default: build_dir/sonoff-dongle-m-otbr.bin)")
    args = parser.parse_args()

    build_dir = args.build_dir.resolve()
    metadata_path = build_dir / "flasher_args.json"
    if not metadata_path.is_file():
        parser.error(f"missing ESP-IDF flash metadata: {metadata_path}")

    metadata = json.loads(metadata_path.read_text(encoding="utf-8"))
    flash_files = metadata.get("flash_files", {})
    if not flash_files:
        parser.error(f"flash metadata has no flash_files: {metadata_path}")

    image_args = []
    for address, relative_name in sorted(flash_files.items(), key=lambda item: int(item[0], 0)):
        image_path = build_dir / relative_name
        if not image_path.is_file():
            parser.error(f"flash image listed by metadata does not exist: {image_path}")
        if "rcp" in image_path.name.lower():
            parser.error(f"refusing to package an RCP image: {image_path.name}")
        image_args.extend([address, str(image_path)])

    settings = metadata.get("flash_settings", {})
    output = (args.output or build_dir / "sonoff-dongle-m-otbr.bin").resolve()
    output.parent.mkdir(parents=True, exist_ok=True)
    command = [sys.executable, "-m", "esptool", "--chip", metadata.get("extra_esptool_args", {}).get("chip", "esp32"), "merge_bin", "--output", str(output)]
    for key in ("flash_mode", "flash_freq", "flash_size"):
        if key in settings:
            command.extend([f"--{key}", settings[key]])
    command.extend(image_args)

    print("Using ESP-IDF flash metadata:", metadata_path)
    print("Merging ESP32 host images to:", output)
    subprocess.run(command, check=True)

    digest = hashlib.sha256(output.read_bytes()).hexdigest()
    checksum_path = output.with_name(output.name + ".sha256")
    checksum_path.write_text(f"{digest}  {output.name}\n", encoding="utf-8")
    print("SHA-256:", digest)
    print("Checksum:", checksum_path)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
