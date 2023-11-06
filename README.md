# CPSC 449 - Project 3

## Usage

First, if you're not already in the Nix shell, you will need to install runtime
dependencies:

```bash
./install_deps.sh
```

This will install packages into the `run` directory, which is specifically an
ephemeral directory for this project.

Then, start all the services:

```bash
foreman start
```

Then, initialize the database and JWT:

```bash
./init.sh
```
