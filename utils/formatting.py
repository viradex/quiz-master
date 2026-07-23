from datetime import datetime, timedelta


def to_ordinal(num: int) -> str:
    """Convert a number to an ordinal (e.g. 1st, 2nd, 3rd, etc)."""
    unique_ordinals = {1: "st", 2: "nd", 3: "rd"}

    # Modulo extracts last two digits from number (e.g. 214 -> 14)
    # If the number is between 10-20, always end in -th
    if 10 <= num % 100 <= 20:
        suffix = "th"

    # Other numbers; modulo extracts last digit and gives respective ordinal
    # with -th as the default for other numbers
    else:
        suffix = unique_ordinals.get(num % 10, "th")

    return f"{num}{suffix}"


def format_datetime(dt: datetime, start_lower: bool = False) -> str:
    """
    Format the datetime given into one of the following formats, respective of current timezone:
    - Today at 9:45 pm
    - Yesterday at 12:34 pm
    - 4 Jun 2026 at 11:31 am
    """
    now = datetime.now()

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
    """Formats ping (round trip time) to include 'ms' at the end."""
    if rtt is None:
        return "-"

    if rtt < 1:
        return "<1ms"

    return f"{round(rtt)}ms"
