"""CLI entrypoint"""

import click
from vk_friends import VKFriends
from vk_friends.constants import FORMATS_SUPPORTED


@click.command()
@click.option(
    "--auth_token",
    "-a",
    type=str,
    help="Vk API authentication token.",
    required=True,
    prompt="Enter your authentication token",
    hide_input=True,
)
@click.option(
    "--user_id",
    "-u",
    type=int,
    help="Id of user, whose friends you want to see.",
    required=True,
)
@click.option(
    "--report_format",
    "-f",
    type=str,
    help="Format of the report. Supported formats are: "
    f"{[format.value for format in FORMATS_SUPPORTED]}. "
    "'csv' by default.",
    default="csv",
)
@click.option(
    "--report_path",
    "-p",
    type=str,
    help="Path to save the report. Can be directory "
    "(in this case, in this directory file named report with "
    "specified extension will appear), or full path to a file. "
    "'./' by default.",
    default="./",
)
@click.option(
    "--api_version",
    "-v",
    type=str,
    help="VK API version. 5.131 by default.",
    default="5.131",
)
@click.option(
    "--request_timeout",
    "-t",
    type=float,
    help="Time (in seconds) period within whick a connection"
    "between client and API server must be established. "
    "If connection wasn't established ServerResponseError "
    "will be raised. 30 by default.",
    default=30,
)
@click.option(
    "--limit",
    "-l",
    type=int,
    help="Number of items to fetch from API. None by default.",
    default=None,
)
@click.option(
    "--offset",
    "-o",
    type=int,
    help="Number of items to discard from the beginning of "
    "friend list. 0 by default.",
    default=0,
)
@click.option(
    "--count",
    "-c",
    type=int,
    help="Number of items to fetch from API per one request." " 100 by default.",
    default=100,
)
def run(
    auth_token: str,
    user_id: str,
    report_format: str,
    api_version: str,
    report_path: str,
    request_timeout: float,
    limit: int,
    offset: int,
    count: int,
):
    """
    Command line interface for generating reports of vk friends of certain user
    """
    print("Creating VKFriends app...")

    app = VKFriends(
        auth_token=auth_token,
        user_id=user_id,
        report_format=report_format,
        report_path=report_path,
        api_version=api_version,
        request_timeout=request_timeout,
        limit=limit,
        offset=offset,
        count=count,
    )

    try:
        app.generate_report()
    except Exception as exception:
        print(
            "Generating of report failed, due to following error:\n"
            + "=" * 50
            + f"\n{exception}"
        )
