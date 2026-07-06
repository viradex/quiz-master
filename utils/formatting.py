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
