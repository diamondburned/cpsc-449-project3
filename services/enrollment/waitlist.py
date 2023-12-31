from typing import Generator
from fastapi import HTTPException
from datetime import datetime
from pydantic import BaseModel
import redis


class WaitlistModel(BaseModel):
    user_id: int
    course_id: int
    section_id: int
    position: int
    date: str


class WaitlistManager:
    _instance = None

    def __new__(cls, *args, **kwargs):
        if not cls._instance:
            cls._instance = super().__new__(cls)
            cls._instance.init(*args, **kwargs)
        return cls._instance

    def init(
        self,
        host="localhost",
        port=6379,
        db=0,
        password=None,
        socket_timeout=None,
    ):
        self.redis_conn = redis.Redis(
            host=host,
            port=port,
            db=db,
            password=password,
            socket_timeout=socket_timeout,
        )

    def extract_user_data(self, user_data) -> WaitlistModel:
        # Extract user data
        current_user_id = int(user_data.get(b"user_id", b"").decode("utf-8"))
        current_course_id = int(user_data.get(b"course_id", b"").decode("utf-8"))
        current_section_id = int(user_data.get(b"section_id", b"").decode("utf-8"))
        current_position = int(user_data.get(b"position", b"").decode("utf-8"))
        current_date = user_data.get(b"date", b"").decode("utf-8")

        return WaitlistModel(
            user_id=current_user_id,
            section_id=current_section_id,
            course_id=current_course_id,
            position=current_position,
            date=current_date,
        )

    def add_to_waitlist(self, user_id, section_id, course_id):
        waitlist_count_for_section = self.get_waitlist_count_for_section(section_id)
        position = waitlist_count_for_section + 1

        # Use a Redis hash to store user details
        user_key = f"user:{user_id}:section:{section_id}"
        user_data = WaitlistModel(
            user_id=user_id,
            section_id=section_id,
            course_id=int(course_id),
            position=position,
            date=datetime.now().strftime("%Y-%m-%d"),
        )

        # Use hset to set each field individually
        for field, value in user_data.dict().items():
            self.redis_conn.hset(user_key, field, value)

        return position

    def get_waitlist_row_for_course(self, course_id):
        # Retrieve waitlist details for all sections
        waitlist_details: list[WaitlistModel] = []
        for key in self.redis_conn.scan_iter():
            user_data = self.redis_conn.hgetall(key)
            extracted_data = self.extract_user_data(user_data)

            if extracted_data.course_id == course_id:
                waitlist_details.append(extracted_data)

        return waitlist_details

    def get_waitlist_row_for_section(self, section_id):
        # Retrieve waitlist details for all sections
        waitlist_details: list[WaitlistModel] = []
        for key in self.redis_conn.scan_iter():
            user_data = self.redis_conn.hgetall(key)
            extracted_data = self.extract_user_data(user_data)

            if extracted_data.section_id == section_id:
                waitlist_details.append(extracted_data)

        return waitlist_details

    def get_waitlist_rows_for_user(self, user_id):
        # Retrieve waitlist details for all sections
        waitlist_details: list[WaitlistModel] = []
        for key in self.redis_conn.keys(f"user:{user_id}:*"):
            user_data = self.redis_conn.hgetall(key)
            extracted_data = self.extract_user_data(user_data)
            waitlist_details.append(extracted_data)

        return waitlist_details

    def get_waitlist_count_for_section(self, section_id):
        # Get the key pattern for the waitlist entries related to the specified section
        waitlist_key_pattern = f"user:*:section:{section_id}"

        # Use SCAN to find all keys matching the pattern
        matching_keys = self.redis_conn.scan_iter(match=waitlist_key_pattern)

        # Count the number of matching keys (i.e., the number of students on the waitlist)
        waitlist_count = sum(1 for _ in matching_keys)

        return waitlist_count

    def get_waitlist_count_for_user(self, user_id):
        # Get the key pattern for the waitlist entries related to the specified user
        waitlist_key_pattern = f"user:{user_id}:section:*"

        # Use SCAN to find all keys matching the pattern
        matching_keys = self.redis_conn.scan_iter(match=waitlist_key_pattern)

        # Count the number of unique section_ids (i.e., the number of sections the user is waitlisted for)
        waitlist_count_for_user = sum(1 for _ in matching_keys)

        return waitlist_count_for_user

    def check_user_on_waitlist_for_section(self, user_id, section_id):
        # Construct the key for the user's waitlist entry
        user_key = f"user:{user_id}:section:{section_id}"

        # Check if the user's key exists in the waitlist
        is_on_waitlist = self.redis_conn.exists(user_key)

        return is_on_waitlist

    def remove_and_get_position(self, user_id, section_id):
        # Construct the key for the user's waitlist entry
        user_key = f"user:{user_id}:section:{section_id}"

        # Get the position of the user in the waitlist before removal
        position = self.redis_conn.hget(user_key, "position")
        if position is None:
            raise HTTPException(status_code=404, detail="User not found in waitlist")

        # Remove the user's entry from the waitlist hash
        self.redis_conn.delete(user_key)

        # Return the position (returns None if user is not found in the waitlist)
        return int(position)

    def decrement_positions_for_others(self, section_id, position):
        user_key_pattern = f"user:*:section:{section_id}"

        # Iterate through all keys matching the pattern
        for user_key in self.redis_conn.scan_iter(match=user_key_pattern):
            user_position = self.redis_conn.hget(user_key, "position")
            assert user_position is not None

            # Decrement position for users with greater position
            if int(user_position) > position:
                self.redis_conn.hincrby(user_key, "position", -1)

    def remove_all_in_section(self, section_id):
        user_key_pattern = f"user:*:section:{section_id}"

        # Iterate through all keys matching the pattern
        for user_key in self.redis_conn.scan_iter(match=user_key_pattern):
            # Remove the user's entry from the waitlist hash
            self.redis_conn.delete(user_key)


# Example usage
# waitlist = WaitlistManager()
# position = waitlist.remove_and_get_position(8, 3)
# waitlist.decrement_positions_for_others(3, position)
# print("scucess")


def get_waitlist_manager() -> Generator[WaitlistManager, None, None]:
    """
    Get a WaitlistManager instance.
    """
    yield WaitlistManager()
