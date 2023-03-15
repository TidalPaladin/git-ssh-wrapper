#!/usr/bin/env python
# -*- coding: utf-8 -*-

from pathlib import Path
from typing import Any, Dict, Optional, Union

import pytest
import yaml

from git_ssh_wrapper import KeyfileEntry


@pytest.fixture(scope="session")
def yaml_factory():
    def func(entries: Dict[str, Union[KeyfileEntry, Dict[str, Any]]], path: Optional[Path] = None):
        result = {
            name: entry.to_dict() if isinstance(entry, KeyfileEntry) else entry for name, entry in entries.items()
        }
        if path:
            with path.open("w") as f:
                yaml.dump(result, f)
        return result

    return func
