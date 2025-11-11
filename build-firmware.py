#!/usr/bin/env python3

import subprocess
import shutil
import os
import sys

# --- Configuration Variables ---
# NOTE: os.path.expanduser('~') reliably expands the tilde (~) in Python
HOME_DIR = os.path.expanduser("~")
ZMK_DIR = os.path.join(HOME_DIR, "z", "zmk")
FIRMWARE_OUT_DIR = os.path.join(HOME_DIR, "z", "zmk-firmware-builds")
LOG_FILE = os.path.join(FIRMWARE_OUT_DIR, "zmk-firmware-builds.log")

# --- Helper Functions ---


def dprint(*args, file=None, **kwargs):
    print(*args, **kwargs)
    if file is not None:
        try:
            sep = kwargs.get("sep", " ")
            end = kwargs.get("end", "\n")
            output_string = sep.join(map(str, args)) + end
            file.write(output_string)
        except Exception as e:
            print(f"Error writing to log file: {e}", file=sys.stderr)


def build_and_copy(
    build_name, board, shield, target, config, log_file=None, extra_args=""
):
    """Runs west build, checks status, and copies the UF2 file to the target name."""

    BUILD = os.path.join(ZMK_DIR, "build", build_name)
    UF2_SOURCE = os.path.join(BUILD, "zephyr", "zmk.uf2")
    UF2_TARGET = os.path.join(FIRMWARE_OUT_DIR, f"{target}.uf2")
    CONFIG_DIR = os.path.join(HOME_DIR, "z", config)

    dprint(f"\n--- Building {target} ---", file=log_file)

    command = [
        "west",
        "build",
        "-s",
        os.path.join(ZMK_DIR, "app"),
        "-d",
        BUILD,
        "-p",
        "-b",
        board,
        "--",
        f"-DSHIELD={shield}",
        f"-DBOARD_ROOT={CONFIG_DIR}",
        f"-DZMK_CONFIG={CONFIG_DIR}",
    ]
    if extra_args:
        command.extend(extra_args.split())

    try:
        # We run the command from the ZMK_DIR because 'west' needs the workspace context
        dprint(f"Executing: {command}", file=log_file)
        subprocess.run(
            command,
            check=True,
            cwd=ZMK_DIR,
            stderr=log_file,
            stdout=log_file,
            capture_output=False,
        )
        dprint("Build successful.", file=log_file)

    except subprocess.CalledProcessError as e:
        print(f"ERROR: Build failed for {target}.", file=log_file)
        print(f"Stdout:\n{e.stdout.decode()}", file=log_file)
        print(f"Stderr:\n{e.stderr.decode()}", file=log_file)
        sys.exit(1)

    try:
        os.makedirs(FIRMWARE_OUT_DIR, exist_ok=True)
        shutil.copy2(UF2_SOURCE, UF2_TARGET)
        dprint(f"Firmware copied to: {UF2_TARGET}", file=log_file)
    except FileNotFoundError:
        dprint(f"ERROR: Could not find built file at {UF2_SOURCE}. Copy failed.")
        sys.exit(1)
    except Exception as e:
        dprint(f"ERROR during file copy: {e}")
        sys.exit(1)


if __name__ == "__main__":
    os.makedirs(FIRMWARE_OUT_DIR, exist_ok=True)
    try:
        with open(LOG_FILE, "w") as f:
            print(f"'west build' output logged to: {LOG_FILE}")

            build_and_copy(
                config="zmk-corne-a741725193-display",
                build_name="eyelash_right",
                board="eyelash_corne_right",
                shield="nice_view",
                target="eyelash_corne_right",
                log_file=f,
            )

            build_and_copy(
                config="zmk-corne-a741725193-display",
                build_name="eyelash_left",
                board="eyelash_corne_left",
                shield="nice_view",
                target="eyelash_corne_left",
                log_file=f,
            )

            build_and_copy(
                config="zmk-corne-a741725193-display",
                build_name="eyelash_reset_left",
                board="eyelash_corne_left",
                shield="settings_reset",
                target="eyelash_reset_left_utility",
                log_file=f,
            )

    except Exception as e:
        print(f"FATAL ERROR in main: {e}")
        sys.exit(1)

    print("\n--- Builds complete! ---")
