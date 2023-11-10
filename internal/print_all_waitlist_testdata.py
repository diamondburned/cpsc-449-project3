import redis

redis_conn = redis.Redis(
    host='localhost',
    port=6379,
    db=0,
    password=None,
    socket_timeout=None
)

def get_all_data():
    # Retrieve all user keys
    user_keys = redis_conn.keys("user:*")

    # Get user data from hashes
    user_data = []
    for user_key in user_keys:
        data = redis_conn.hgetall(user_key)
        user_data.append({
            "user_key": user_key.decode("utf-8"),
            "data": {key.decode("utf-8"): value.decode("utf-8") for key, value in data.items()}
        })

    # Retrieve all waitlist keys
    waitlist_keys = redis_conn.keys("waitlist:section:*")

    # Get waitlist data from sorted sets
    waitlist_data = []
    for waitlist_key in waitlist_keys:
        data = redis_conn.zrange(waitlist_key, 0, -1, withscores=True)
        waitlist_data.append({
            "waitlist_key": waitlist_key.decode("utf-8"),
            "data": [{user_key.decode("utf-8"): position} for user_key, position in data]
        })

    return user_data, waitlist_data

# Get all data from Redis
all_user_data, all_waitlist_data = get_all_data()

# Print the results
print("User Data:")
for user in all_user_data:
    print(user)

print("\nWaitlist Data:")
for waitlist in all_waitlist_data:
    print(waitlist)