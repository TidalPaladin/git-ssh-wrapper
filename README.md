# git-ssh-wrapper

Implements a Python wrapper that enables specific identity files to be used when cloning specific repos.
If no identity is specified a generic SSH command will be used.

## Usage

The association of keyfiles and repositories is configured through a YAML file

```yaml
repo1:
  url: "org1/repo1.git"
  identity: "id_rsa_repo1"

repo2:
  url: "org2/repo2.git"
  identity: "id_rsa_repo2"
```

You can then configure `git` to use the wrapper with

```bash
export GIT_SSH_COMMAND='wrapped-ssh'
```

or

```bash
export GIT_SSH_COMMAND='python -m git_ssh_wrapper'
```

### CLI Options

```
usage: ssh-wrapper [-h] [-i IDENTITY_ROOT] [-d] keyfile command [command ...]

SSH wrapper for private cloning

positional arguments:
  keyfile               Path to the SSH key config
  command               SSH command

options:
  -h, --help            show this help message and exit
  -i IDENTITY_ROOT, --identity-root IDENTITY_ROOT
                        Path to the directory containing the SSH identities
  -d, --dry-run         Do not actually run the SSH command
```
