#!/usr/bin/env python
# -*- coding: utf-8 -*-
import subprocess
from dataclasses import dataclass
from pathlib import Path
from typing import Any, Dict, Set

import yaml


@dataclass(frozen=True)
class KeyfileEntry:
    repo: str
    identity: Path

    def should_run(self, *command: str) -> bool:
        cmd = " ".join(command)
        return self.repo in cmd

    def run(self, *command: str) -> None:
        if not self.should_run(*command):
            raise ValueError(f"Command {command} does not match {self.repo}")  # pragma: no cover
        if not self.identity.is_file():
            raise FileNotFoundError(self.identity)  # pragma: no cover
        subprocess.run(
            ["ssh", "-i", str(self.identity), *command],
            check=True,
            shell=True,
        )

    @classmethod
    def from_dict(cls, identity_root: Path, data: Dict[str, Any]) -> "KeyfileEntry":
        return cls(
            repo=data["repo"],
            identity=identity_root / data["identity"],
        )

    def to_dict(self) -> Dict[str, str]:
        return {
            "repo": self.repo,
            "identity": self.identity.name,
        }

    @classmethod
    def from_yaml(cls, identity_root: Path, path: Path) -> Set["KeyfileEntry"]:
        if not path.is_file():
            raise FileNotFoundError(f"Keyfile {path} not found")  # pragma: no cover
        if not identity_root.is_dir():
            raise NotADirectoryError(f"Identity root {identity_root} is not a directory")  # pragma: no cover

        with path.open() as f:
            data = yaml.safe_load(f)
        if not isinstance(data, dict):
            raise ValueError(f"Expected a dict, got {type(data)}")  # pragma: no cover
        return {cls.from_dict(identity_root, entry) for entry in data.values()}

    @classmethod
    def to_yaml(cls, entries: Dict[str, "KeyfileEntry"], path: Path) -> None:
        result = {name: entry.to_dict() for name, entry in entries.items()}
        with path.open("w") as f:
            yaml.safe_dump(result, f, default_flow_style=False)
