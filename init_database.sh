#!/bin/sh
set -e

if ! PATH="$PATH":run/bin command -v litefs >/dev/null 2>&1; then
	echo "litefs isn't even installed, did you run ./install_deps.sh?" >&2
	exit 1
fi

echo "Initializing enrollment database..."
python3 -m services.enrollment.schema_init
python3 -m services.enrollment.dynamodb.flush_tables
python3 -m services.enrollment.dynamodb.create_tables
python3 -m services.enrollment.dynamodb.insert_testdata
python3 -m services.enrollment.redis.flush_store
python3 -m services.enrollment.redis.insert_testdata
echo

echo "Initializing authentication database..."
python3 -m services.authentication.schema_init
echo
