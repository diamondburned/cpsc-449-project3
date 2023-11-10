import redis

redis_conn = redis.Redis(
            host='localhost',
            port=6379,
            db=0,
            password=None,
            socket_timeout=None
        )

def add_to_waitlist(user_id, section_id, position, date, course_id):
    # Use a Redis hash to store user details
    user_key = f"user:{user_id}"
    user_data = {
        "section_id": section_id,
        "position": position,
        "date": date,
        "course_id": course_id 
    }

    # Use hset to set each field individually
    for field, value in user_data.items():
        redis_conn.hset(user_key, field, value)

    # Use a Redis sorted set to store the waitlist with position as the score
    waitlist_key = f"waitlist:section:{section_id}"
    redis_conn.zadd(waitlist_key, {user_key: position})

# Test data
test_data = [
    (8, 3, 1, '2023-09-15', 2),
    (9, 2, 1, '2023-09-15', 1),
    (10, 4, 1, '2023-09-15', 2),
    (11, 1, 1, '2023-09-15', 1),
    (12, 3, 2, '2023-09-15', 2),
    (13, 1, 2, '2023-09-15', 1),
    (14, 2, 2, '2023-09-15', 1)
]

# Insert test data into Redis
for user_id, section_id, position, date, course_id in test_data:
    add_to_waitlist(user_id, section_id, position, date, course_id)

print("Test data inserted into Redis.")




