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
    now = datetime.now(dt.tzinfo) if dt.tzinfo else datetime.now()

    if dt.date() == now.date():
        day = "today" if start_lower else "Today"
    elif dt.date() == (now.date() - timedelta(days=1)):
        day = "yesterday" if start_lower else "Yesterday"
    else:
        day = f"{dt.day} {dt.strftime('%b %Y')}"

    # 12-hour format without leading zero
    time = dt.strftime("%I:%M %p").lstrip("0").lower()
    return f"{day}, {time}"
