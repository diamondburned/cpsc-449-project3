#!/bin/sh
set -e

echo "Initializing enrollment database..."
python3 -m services.enrollment.schema_init
