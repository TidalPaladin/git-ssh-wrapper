#!/usr/bin/env python
# -*- coding: utf-8 -*-
import importlib.metadata

from .keyfile import KeyfileEntry


__version__ = importlib.metadata.version("git-ssh-wrapper")

__all__ = [
    "KeyfileEntry",
]
