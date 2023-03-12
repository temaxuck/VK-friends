# Improvado-Interview-Assignment

vkfriends
=============

Command line interface for generating reports of vk friends of certain
user 

Installation
------------
```
git clone https://github.com/temaxuck/Improvado-Interview-Assignment.git
cd  Improvado-Interview-Assignment
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
    