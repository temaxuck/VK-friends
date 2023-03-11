"""field_handlers.py
Module contains callback functions that
handle specific field of `user` object that is to be prepared
for writing in report file
"""

import typing as t


def bdate_handler(value: str) -> str:
    """bdate field handler.

    Args:
        value (str): date in DD.MM.YYYY format or if year is not
        specified DD.MM format

    Returns:
        str: date in ISO format.
    """
    if not value:
        return None

    date = value.split(".")
    if len(date) == 2:
        return f"--{date[1].zfill(2)}-{date[0].zfill(2)}T00:00:00.000"
    return f"{date[2]}-{date[1].zfill(2)}-{date[0].zfill(2)}T00:00:00.000"
