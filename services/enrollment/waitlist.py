import redis
from datetime import datetime

class WaitlistManager:
    _instance = None

    def __new__(cls, *args, **kwargs):
        if not cls._instance:
            cls._instance = super().__new__(cls)
            cls._instance.init(*args, **kwargs)
        return cls._instance

    def init(self, host='localhost', port=6379, db=0, password=None, socket_timeout=None):
        self.redis_conn = redis.Redis(
            host=host,
            port=port,
            db=db,
            password=password,
            socket_timeout=socket_timeout
        )

    def add_to_waitlist(self, user_id, section_id, position, course_id):
        position = position + 1

        # Use a Redis hash to store user details
        user_key = f"user:{user_id}"
        user_data = {
            "section_id": section_id,
            "position": position,
            "date": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            "course_id": course_id 
        }

        # Use hset to set each field individually
        for field, value in user_data.items():
            self.redis_conn.hset(user_key, field, value)

        # Use a Redis sorted set to store the waitlist with position as the score
        waitlist_key = f"waitlist:section:{section_id}"
        self.redis_conn.zadd(waitlist_key, {user_key: position})

        return position
    
    def get_waitlist_for_section(self, section_id):
        # Retrieve the waitlist for a specific section from the sorted set
        waitlist_key = f"waitlist:section:{section_id}"
        waitlist = self.redis_conn.zrange(waitlist_key, 0, -1, withscores=True)

        # Get user details from the hash using the user keys
        waitlist_details = []
        for user_key, position in waitlist:
            user_data = self.redis_conn.hgetall(user_key)
            user_id = int(user_key.split(b":")[1])  # Decode and use bytes split
            section_id = int(user_data[b"section_id"])
            position = int(user_data[b"position"])
            date = user_data[b"date"].decode("utf-8")
            course_id = int(user_data[b"course_id"])  # Retrieve course_id
            waitlist_details.append({
                "user_id": user_id,
                "section_id": section_id,
                "position": position,
                "date": date,
                "course_id": course_id  # Include course_id in the result
            })
        return waitlist_details
    
    def get_waitlist_for_course(self, course_id):
        # Retrieve waitlist details for all sections
        waitlist_details = []
        for key in self.redis_conn.scan_iter(match=b"user:*"):
            user_data = self.redis_conn.hgetall(key)
            user_id = int(key.split(b":")[1])

            # Extract course_id and section_id from user_data
            current_course_id = int(user_data.get(b'course_id', b'').decode('utf-8'))
            current_section_id = int(user_data.get(b'section_id', b'').decode('utf-8'))

            if current_course_id == course_id:
                waitlist_details.append({
                    "waitlist.user_id": user_id,
                    "sections.id": current_section_id,
                })

        return waitlist_details

    def get_waitlist_count_for_section(self, section_id):
        # Get the number of students on the waitlist for a specific section
        waitlist_key = f"waitlist:section:{section_id}"
        return self.redis_conn.zcard(waitlist_key)
    
    def get_waitlist_count_for_user(self, user_id):
        # Get the number of sections a student is waitlisted for
        user_key = f"user:{user_id}"
        sections_waitlisted = set()

        # Check all waitlist keys for the user
        for key in self.redis_conn.scan_iter(match=b"waitlist:section:*"):
            if self.redis_conn.zrank(key, user_key) is not None:
                section_id = int(key.split(b":")[-1].decode("utf-8"))
                sections_waitlisted.add(section_id)

        return len(sections_waitlisted)
    
    
    


# Example usage
# waitlist_manager = WaitlistManager()
# top_players = waitlist_manager.get_top_players()
# print(top_players)





