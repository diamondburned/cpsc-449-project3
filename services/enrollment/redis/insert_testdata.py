import redis

redis_conn = redis.Redis(
    host="localhost", port=6379, db=0, password=None, socket_timeout=None
)


def add_to_waitlist(user_id, section_id, course_id, position, date):
    # Use a Redis hash to store user details
    user_key = f"user:{user_id}:section:{section_id}"
    user_data = {
        "user_id": user_id,
        "section_id": section_id,
        "position": position,
        "date": date,
        "course_id": course_id,
    }

    # Use hset to set each field individually
    for field, value in user_data.items():
        redis_conn.hset(user_key, field, value)


# Test data
test_data = [
    (8, 3, 2, 1, "2023-09-15"),
    (9, 2, 1, 1, "2023-09-15"),
    (10, 4, 2, 1, "2023-09-15"),
    (11, 1, 1, 1, "2023-09-15"),
    (12, 3, 2, 2, "2023-09-15"),
    (13, 1, 1, 2, "2023-09-15"),
    (14, 2, 1, 2, "2023-09-15"),
]

# Insert test data into Redis
for user_id, section_id, course_id, position, date in test_data:
    add_to_waitlist(user_id, section_id, course_id, position, date)

print("Test data inserted into Redis.")
