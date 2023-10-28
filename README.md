# CPSC 449 - Project 2

## Setting Up

Install the following dependencies:

- Python 3 w/ virtualenv
- Krakend
- LiteFS

All of these dependencies should be in your `PATH` variable for `Procfile` to
work.

Then, install the Python dependencies:

```bash
pip install -r requirements.txt
```

## Usage

First, if you're not already in the Nix shell, you will need to install Krakend
and LiteFS:

```bash
./install_deps.sh
```

This will install Krakend and LiteFS into the `run` directory, which is
specifically an ephemeral directory for this project.

Then, start all the services:

```bash
foreman start
```

Then, initialize the database and JWT:

```bash
./init.sh
```
