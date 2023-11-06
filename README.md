# CPSC 449 - Project 3

## Usage

First, you will need to install runtime dependencies:

```bash
./init.sh # also works in Nix shell
```

This will install packages into the `run` directory, which is specifically an
ephemeral directory for this project.

Then, start all the services:

```bash
foreman start
```

Then, initialize the database:

```bash
./init_database.sh
```
