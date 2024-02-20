# VK-friends utility

vkfriends
=============

Command line interface for generating reports of vk friends of a certain
user 

Installation
------------
```
git clone https://github.com/temaxuck/VK-friends.git
cd  VK-friends
python -m pip install .
```

Usage
-----
    $ vkfriends --help
        Usage: vkfriends [OPTIONS]

        Command line interface for generating reports of vk friends of certain user

        Options:
        -a, --auth_token TEXT        Vk API authentication token.  [required]
        -u, --user_id INTEGER        Id of user, whose friends you want to see.
                                    [required]
        -f, --report_format TEXT     Format of the report. Supported formats are:
                                    ['csv', 'tsv', 'json']. 'csv' by default.
        -p, --report_path TEXT       Path to save the report. Can be directory (in
                                    this case, in this directory file named report
                                    with specified extension will appear), or full
                                    path to a file. './' by default.
        -v, --api_version TEXT       VK API version. 5.131 by default.
        -t, --request_timeout FLOAT  Time (in seconds) period within whick a
                                    connectionbetween client and API server must be
                                    established. If connection wasn't established
                                    ServerResponseError will be raised. 30 by
                                    default.
        -l, --limit INTEGER          Number of items to fetch from API. None by
                                    default.
        -o, --offset INTEGER         Number of items to discard from the beginning
                                    of friend list. 0 by default.
        -c, --count INTEGER          Number of items to fetch from API per one
                                    request. 100 by default.
        --help                       Show this message and exit.
    
Authentication token
--------------------
To get authentication token I recommend using official application: https://vkhost.github.io/

Example usage
-------------
To generate report for user_id = 205387401 in json format, with offset = 30 and limit = 20 run this command:

    $ vkfriends -u 205387401 -f json -l 20 -o 30 
    Enter your authentication token: 
    Creating VKFriends app...
    Creating file ./report.json
    Fetched 20 out of 87 friends
    Saving report into ./report.json
