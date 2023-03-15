#!/usr/bin/env python
# -*- coding: utf-8 -*-
import runpy
import sys
from dataclasses import replace
from pathlib import Path

import pytest

from git_ssh_wrapper import KeyfileEntry


def test_entrypoint():
    import subprocess

    subprocess.run(["pdm", "run", "wrapped-ssh", "--help"], check=True)


class TestMain:
    @pytest.fixture(autouse=True)
    def mock_run(self, mocker):
        return mocker.patch("subprocess.run")

    def _setup_identity_files(self, tmp_path, keyfiles):
        _keyfiles = {}
        for name, k in keyfiles.items():
            identity = Path(tmp_path, k.identity)
            identity.touch()
            keyfile = replace(k, identity=identity)
            _keyfiles[name] = keyfile
        return _keyfiles

    @pytest.mark.parametrize("dry_run", [True, False])
    @pytest.mark.parametrize(
        "keyfiles,command,exp",
        [
            pytest.param(
                {
                    "repo1": KeyfileEntry(repo="source/repo1.git", identity=Path("identity1")),
                    "repo2": KeyfileEntry(repo="source/repo2.git", identity=Path("identity2")),
                },
                ["git", "clone", "ssh://git@github.com/source/repo1.git"],
                Path("identity1"),
            ),
            pytest.param(
                {
                    "repo1": KeyfileEntry(repo="source/repo1.git", identity=Path("identity1")),
                    "repo2": KeyfileEntry(repo="source/repo2.git", identity=Path("identity2")),
                },
                ["git", "clone", "ssh://git@github.com/source/repo2.git"],
                Path("identity2"),
            ),
            pytest.param(
                {
                    "repo1": KeyfileEntry(repo="source/repo1.git", identity=Path("identity1")),
                    "repo2": KeyfileEntry(repo="source/repo2.git", identity=Path("identity2")),
                },
                ["git", "run", "command", "source/repo2.git"],
                Path("identity2"),
            ),
            pytest.param(
                {
                    "repo1": KeyfileEntry(repo="source/repo1.git", identity=Path("identity1")),
                    "repo2": KeyfileEntry(repo="source/repo2.git", identity=Path("identity2")),
                },
                ["git", "clone", "ssh://git@github.com/source/repo3.git"],
                None,
            ),
        ],
    )
    def test_run(self, mock_run, tmp_path, yaml_factory, keyfiles, command, exp, dry_run):
        keyfile_path = Path(tmp_path, "keyfile.yaml")
        yaml_factory(keyfiles, path=keyfile_path)
        keyfiles = self._setup_identity_files(tmp_path, keyfiles)
        identity = Path(tmp_path, exp) if exp is not None else None

        sys.argv = [
            sys.argv[0],
            str(keyfile_path),
            "-i",
            str(tmp_path),
        ]
        if dry_run:
            sys.argv.append("--dry-run")
        sys.argv = sys.argv + command

        runpy.run_module(
            "git_ssh_wrapper",
            run_name="__main__",
            alter_sys=True,
        )

        if dry_run:
            mock_run.assert_not_called()
        else:
            mock_run.assert_called_once()
            called_command = mock_run.call_args.args[0]
            if identity:
                assert called_command[:3] == ["ssh", "-i", str(identity)]
                assert called_command[3:] == command
            else:
                assert called_command[:1] == ["ssh"]
                assert called_command[1:] == command
