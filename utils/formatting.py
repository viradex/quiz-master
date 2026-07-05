def to_ordinal(num: int) -> str:
    unique_ordinals = {1: "st", 2: "nd", 3: "rd"}

    if 10 <= num % 100 <= 20:
        suffix = "th"
    else:
        suffix = unique_ordinals.get(num % 10, "th")

    return f"{num}{suffix}"
