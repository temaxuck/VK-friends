"""vk_friends module is used to generate reports of vk users
    that a specific user has as friends. Accessing information through
    public vk API. 
    
    Getting Started:
        To create app you should create VKFriends instance in your module.
        Usually it looks like this:
        
            from vk_friends import VKFriends
            
            app = VKFriends(
                auth_token=token,
                user_id=user_id,
                report_format="tsv",
                report_path=".",
            )
            
            
        Where token is authentication token (see dev.vk.com, how to get one),
        user_id is id of the user whose friends you want to see through
        
        To generate report use generate_report function:

            app.generate_report()
         
            
        You also can manually incrementally fetch friend list using 
        fetch_friend_list method() which returns python generator object.
        Example usage:
        
            for fetch_response in app.fetch_friend_list():
                
                print(fetch_response["data"]["response"]["items"])
           
"""

from .app import VKFriends
from .constants import FORMATS_SUPPORTED

__all__ = ["VKFriends", "FORMATS_SUPPORTED"]
