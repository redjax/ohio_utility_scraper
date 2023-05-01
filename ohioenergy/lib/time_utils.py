import arrow

default_date_fmt = "YYYY-MM-DD_HH:MM:SS"


def get_ts(fmt: str = default_date_fmt) -> arrow.Arrow:
    ts = arrow.now().format(fmt=fmt)

    return ts


def get_date(fmt: str = "YYYY-MM-DD") -> arrow.Arrow:
    date = arrow.now().format(fmt=fmt)

    return date
