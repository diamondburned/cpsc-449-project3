import redis

# Connect to Redis
redis_conn = redis.Redis(
    host='localhost',
    port=6379,
    db=0,
    password=None,
    socket_timeout=None
)

# Flush all data in Redis
redis_conn.flushall()

print("Flushed existing data from Redis.")