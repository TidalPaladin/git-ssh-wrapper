#!/usr/bin/env python
# -*- coding: utf-8 -*-

from dataclasses import replace
from pathlib import Path

import pytest
import yaml

from git_ssh_wrapper import KeyfileEntry


class TestKeyfile:
    def test_from_yaml(self, tmp_path, yaml_factory):
        path = tmp_path / "keyfile.yaml"
        keyfiles = {
            "repo1": KeyfileEntry(repo="repo1", identity=Path(tmp_path, "identity1")),
            "repo2": KeyfileEntry(repo="repo2", identity=Path(tmp_path, "identity2")),
        }
        yaml_factory(keyfiles, path=path)
        result = KeyfileEntry.from_yaml(tmp_path, path)
        assert isinstance(result, set)
        assert len(result) == 2
        assert result == set(keyfiles.values())

    def test_to_yaml(self, tmp_path):
        path = tmp_path / "keyfile.yaml"
        keyfiles = {
            "repo1": KeyfileEntry(repo="repo1", identity=Path(tmp_path, "identity1")),
            "repo2": KeyfileEntry(repo="repo2", identity=Path(tmp_path, "identity2")),
        }
        KeyfileEntry.to_yaml(keyfiles, path)
        with path.open() as f:
            result = yaml.load(f, Loader=yaml.SafeLoader)
        assert isinstance(result, dict)
        assert len(result) == 2
        assert result == {name: entry.to_dict() for name, entry in keyfiles.items()}

    @pytest.mark.parametrize(
        "keyfiles,command,exp",
        [
            pytest.param(
                {
                    KeyfileEntry(repo="source/repo1.git", identity=Path("identity1")),
                    KeyfileEntry(repo="source/repo2.git", identity=Path("identity2")),
                },
                ["git", "clone", "ssh://git@github.com/source/repo1.git"],
                Path("identity1"),
            ),
            pytest.param(
                {
                    KeyfileEntry(repo="source/repo1.git", identity=Path("identity1")),
                    KeyfileEntry(repo="source/repo2.git", identity=Path("identity2")),
                },
                ["git", "clone", "ssh://git@github.com/source/repo2.git"],
                Path("identity2"),
            ),
            pytest.param(
                {
                    KeyfileEntry(repo="source/repo1.git", identity=Path("identity1")),
                    KeyfileEntry(repo="source/repo2.git", identity=Path("identity2")),
                },
                ["git", "run", "command", "source/repo2.git"],
                Path("identity2"),
            ),
            pytest.param(
                {
                    KeyfileEntry(repo="source/repo1.git", identity=Path("identity1")),
                    KeyfileEntry(repo="source/repo2.git", identity=Path("identity2")),
                },
                ["git", "clone", "ssh://git@github.com/source/repo3.git"],
                None,
            ),
        ],
    )
    def test_should_run(self, keyfiles, command, exp):
        result = {entry.identity for entry in keyfiles if entry.should_run(*command)}
        assert next(iter(result), None) == exp

    @pytest.mark.parametrize(
        "keyfile,command",
        [
            pytest.param(
                KeyfileEntry(repo="source/repo1.git", identity=Path("identity1")),
                ["git", "clone", "ssh://git@github.com/source/repo1.git"],
            ),
            pytest.param(
                KeyfileEntry(repo="source/repo2.git", identity=Path("identity2")),
                ["git", "clone", "ssh://git@github.com/source/repo2.git"],
            ),
            pytest.param(
                KeyfileEntry(repo="source/repo1.git", identity=Path("identity1")),
                ["git", "clone", "ssh://git@github.com/source/repo2.git"],
                marks=pytest.mark.xfail(raises=ValueError, strict=True),
            ),
        ],
    )
    def test_run(self, tmp_path, mocker, keyfile, command):
        identity = Path(tmp_path, keyfile.identity)
        identity.touch()
        keyfile = replace(keyfile, identity=identity)
        m = mocker.patch("subprocess.run")
        keyfile.run(*command)
        m.assert_called_once()
        call = m.call_args
        assert call.kwargs == {"check": True}
        assert len(call.args) == 1

        called_command = call.args[0]
        assert called_command[:3] == ["ssh", "-i", str(identity)]
        assert called_command[3:] == command
