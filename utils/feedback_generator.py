import random

# Feedback messages definition, with weighting
# {nickname} is the name of the player in front
# {points} is the amount of points the player is behind the player in front
MESSAGES: dict[str, tuple[list[str], list[int]]] = {
    "first": (
        [
            "You finished on the podium and took first place!",
            "You took first place! Congratulations!",
            "First place, well played!",
            "You claimed the top spot! Try not to brag too much ;)",
        ],
        [50, 30, 15, 5],
    ),
    "podium": (
        [
            "You finished on the podium and were {points} points behind {nickname}!",
            "Great finish! You were {points} points behind {nickname}.",
            "A podium finish, nice! {points} points separated you from {nickname}.",
        ],
        [60, 30, 10],
    ),
    "tie_podium": (
        [
            "You tied with {nickname} ON THE PODIUM! Wow!",
            "You finished on the podium AND tied with {nickname}! If only you were just a millisecond faster on one of those questions...",
        ],
        [60, 40],
    ),
    "close_podium": (
        [
            "You finished on the podium and were only {points} points behind {nickname}! So close!",
            "A podium finish! Just {points} points behind {nickname}. Let's see if you can beat them next time...",
        ],
        [85, 15],
    ),
    "regular": (
        [
            "You were {points} points behind {nickname}!",
            "You finished {points} points behind {nickname}!",
            "{nickname} finished {points} points ahead this time!",
        ],
        [60, 30, 10],
    ),
    "tie_regular": (
        [
            "You tied with {nickname}! Wow!",
            "Amazing tie with {nickname}! If only you were just a millisecond faster on one of those questions...",
        ],
        [60, 40],
    ),
    "close_regular": (
        [
            "You were only {points} points behind {nickname}! So close!",
            "Aww, just {points} points behind {nickname}...",
        ],
        [90, 10],
    ),
    "last": (
        [
            "Everyone has an off day. Better luck next time!",
            "Don't give up; your next run could be a winner!",
            "Every dog has its day; keep at it!",
            "Try not to become enemies with {nickname} ;)",
        ],
        [50, 30, 15, 5],
    ),
}


def feedback_generator(
    is_podium: bool,
    is_first: bool,
    is_last: bool,
    behind_nickname: str | None,
    behind_points: int | None,
) -> str:
    """Generate a personalized random feedback message based on certain cases."""
    is_close = behind_points is not None and behind_points < 50
    is_tie = behind_points is not None and behind_points == 0

    if is_first:
        text = _get_random_message("first", behind_nickname, behind_points)
    elif is_podium and is_tie:
        text = _get_random_message("tie_podium", behind_nickname, behind_points)
    elif is_podium and is_close:
        text = _get_random_message("close_podium", behind_nickname, behind_points)
    elif is_podium:
        text = _get_random_message("podium", behind_nickname, behind_points)
    elif is_last:
        text = _get_random_message("last", behind_nickname, behind_points)
    elif is_tie:
        text = _get_random_message("tie_regular", behind_nickname, behind_points)
    elif is_close:
        text = _get_random_message("close_regular", behind_nickname, behind_points)
    else:
        text = _get_random_message("regular", behind_nickname, behind_points)

    return text


def _get_random_message(message_type: str, nickname: str, points: str | int) -> str:
    """Get a random message from the MESSAGES constant based on the message type, and format it."""
    messages, weights = MESSAGES[message_type]

    # choices() always returns a list, even if k=1, therefore get first element
    return random.choices(messages, weights=weights)[0].format(
        nickname=nickname, points=points
    )
