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

First, start all the services:

```bash
foreman start
```

Then, initialize the database and JWT:

```bash
./init.sh
```
