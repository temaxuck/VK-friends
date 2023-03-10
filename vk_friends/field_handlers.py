import typing as t


def bdate_handler(value: str) -> str:
    if not value:
        return None

    date = value.split(".")
    if len(date) == 2:
        return f"--{date[1].zfill(2)}-{date[0].zfill(2)}T00:00:00.000"
    return f"{date[2]}-{date[1].zfill(2)}-{date[0].zfill(2)}T00:00:00.000"
