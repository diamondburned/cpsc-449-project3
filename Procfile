gateway: USAGE_DISABLE=1 krakend run --port $PORT --config cfg/krakend.json
enrollment_service: uvicorn --port $PORT services.enrollment.api:app --reload
authentication_service: uvicorn --port $PORT services.authentication.api:app --reload
authentication_db_primary: litefs mount --config cfg/authentication/primary.yml
authentication_db_secondary1: litefs mount --config cfg/authentication/secondary1.yml
authentication_db_secondary2: litefs mount --config cfg/authentication/secondary2.yml
