#!/usr/bin/env python
# -*- coding: utf-8 -*-
from git_ssh_wrapper import __version__


def test_version():
    assert isinstance(__version__, str)
