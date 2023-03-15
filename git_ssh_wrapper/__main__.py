#!/usr/bin/env python
# -*- coding: utf-8 -*-
import argparse
import subprocess
from pathlib import Path

from . import KeyfileEntry


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(prog="ssh-wrapper", description="SSH wrapper for private cloning")
    parser.add_argument(
        "-i",
        "--identity-root",
        type=Path,
        default=Path.home() / ".ssh",
        help="Path to the directory containing the SSH identities",
    )
    parser.add_argument(
        "-d", "--dry-run", default=False, action="store_true", help="Do not actually run the SSH command"
    )
    parser.add_argument("keyfile", type=Path, help="Path to the SSH key config")
    parser.add_argument("command", type=str, nargs="+", help="SSH command")
    return parser.parse_args()


def main(args: argparse.Namespace):
    if not args.keyfile.is_file():
        raise FileNotFoundError(f"Keyfile {args.keyfile} not found")  # pragma: no cover

    possible_keys = KeyfileEntry.from_yaml(args.identity_root, args.keyfile)
    for key in possible_keys:
        if key.should_run(*args.command):
            if args.dry_run:
                print(f"Would run {args.command} with {key}")
            else:
                key.run(*args.command)
            return
    else:
        if args.dry_run:
            print(f"Would run {args.command} with default key")
        else:
            cmd = ["ssh", *args.command]
            subprocess.run(cmd, check=True)


def entrypoint():
    main(parse_args())


if __name__ == "__main__":
    entrypoint()
