gateway: USAGE_DISABLE=1 krakend run --port $PORT --config cfg/krakend.json
enrollment_service: uvicorn --port $PORT services.enrollment.api:app --reload
