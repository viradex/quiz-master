"""
formatting.py

Provides functions for converting values into user-friendly data.
"""

from datetime import datetime, timedelta


def to_ordinal(number: int) -> str:
    """
    Converts an integer number to an ordinal (e.g. 1st, 2nd, 3rd, etc).

    Arguments:
        number: The number to convert to an ordinal. An integer is used as whole numbers are easier
            to work with for ordinals, and are generally used more than floats as ordinals are for
            user-facing values.

    Returns:
        A string of the number as an ordinal. A string is used rather than an integer as an integer
        cannot represent the ordinal part of the number (e.g. -th).
    """
    # Ordinals that do not have -th suffixed
    unique_ordinals = {1: "st", 2: "nd", 3: "rd"}

    # Modulo extracts last two digits from number (e.g. 214 -> 14)
    # If the number is between 10-20, always end in -th
    if 10 <= number % 100 <= 20:
        suffix = "th"

    # Other numbers; modulo extracts last digit and gives respective ordinal
    # with -th as the default for other numbers.
    else:
        suffix = unique_ordinals.get(number % 10, "th")

    return f"{number}{suffix}"


def format_datetime(dt: datetime, start_lower: bool = False) -> str:
    """
    Formats the datetime given into one of the following formats:
    - Today, 9:45 pm
    - Yesterday, 12:34 pm
    - 4 Jun 2026, 11:31 am

    Arguments:
        dt: The time and date to format into a user-friendly version. A datetime is used as it provides
            metadata and easier comparisons with other datetimes that makes formatting easier compared
            to a string, for example.

        start_lower: A boolean determining whether to start 'Today' or 'Yesterday' with a lowercase
            letter. Defaults to False.

    Returns:
        A string of the formatted datetime. A string is used opposed to another value such as a datetime
        or integer as the string displays the user-friendly modifications clearly without extra issues
        or later formatting needed.
    """
    # Get the datetime now for comparisons against the datetime given
    now = datetime.now().astimezone()

    if dt.date() == now.date():
        # Date is today in this timezone
        day = "today" if start_lower else "Today"
    elif dt.date() == (now.date() - timedelta(days=1)):
        # Date was yesterday in this timezone (1 day ago)
        day = "yesterday" if start_lower else "Yesterday"
    else:
        # Every other date
        day = f"{dt.day} {dt.strftime('%b %Y')}"

    # 12-hour format without leading zero
    time = dt.strftime("%I:%M %p").lstrip("0").lower()
    return f"{day}, {time}"


def format_ping(rtt: float | None) -> str:
    """
    Formats the ping, or round-trip time, to include 'ms' at the end. Also, if the round-trip time
    provided is less than 1, the value returned is '<1' visually. If the round-trip time provided
    is None, a dash '-' is returned.

    Arguments:
        rtt: The round-trip time in milliseconds to convert to a user-friendly value, or None if no
            value was calculated yet. A float is used as it represents sub-millisecond precision which
            is needed for if the value is below 1ms.

    Returns:
        A string representing the user-friendly round-trip time. A string is used as the formatting
        used, including the 'ms' and '<1' text, if included, requires a string.
    """
    # Round-trip time not provided yet
    if rtt is None:
        return "-"

    # Better to show <1ms rather than 0ms, as 0ms implies there is absolutely
    # no lag when that isn't possible.
    if rtt < 1:
        return "<1ms"

    return f"{round(rtt)}ms"
