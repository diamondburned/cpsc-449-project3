#!/bin/sh
set -e

echo "Initializing enrollment database..."
python3 -m services.enrollment.schema_init
echo

echo "Initializing authentication database..."
python3 -m services.authentication.schema_init
echo

echo "Initializing new JWT keys..."
python3 -m internal.jwt_init
