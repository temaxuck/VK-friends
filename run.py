import os

from vk_friends import VKFriends

token = os.getenv("TOKEN")
user_id = os.getenv("TEST_USER_ID")

if __name__ == "__main__":
    app = VKFriends(
        auth_token=token,
        user_id=user_id,
        report_format="csv",
        report_path=".",
    )

    app.generate_report()
