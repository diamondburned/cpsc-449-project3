#!/bin/sh
set -e

if ! PATH="$PATH":run/bin command -v litefs >/dev/null 2>&1; then
	echo "litefs isn't even installed, did you run ./install_deps.sh?" >&2
	exit 1
fi

echo "Initializing enrollment database..."
python3 -m services.enrollment.schema_init
echo

echo "Initializing authentication database..."
python3 -m services.authentication.schema_init
echo

echo "Initializing redis database..."
python3 internal/flush_redis_store.py
python3 internal/insert_redis_waitlist_testdata.py
echo

echo "Initializing dyanmodb database..."
python3 internal/flush_dynamo_tables.py
python3 internal/create_dynamo_tables.py
python3 internal/insert_dynamo_testdata.py
echo