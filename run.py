import os

from vk_friends import VKFriends
from vk_friends import FORMATS_SUPPORTED

token = os.getenv("TOKEN")
user_id = os.getenv("TEST_USER_ID")

if __name__ == "__main__":
    app = VKFriends(
        auth_token=token, user_id=user_id, report_format=FORMATS_SUPPORTED.JSON
    )

    app.generate_report()
