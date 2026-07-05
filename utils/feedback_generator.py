import random

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


def get_random_message(message_type: str, nickname: str, points: str | int) -> str:
    messages, weights = MESSAGES[message_type]

    return random.choices(messages, weights=weights)[0].format(
        nickname=nickname, points=points
    )


def feedback_generator(
    is_podium: bool,
    is_first: bool,
    is_last: bool,
    behind_nickname: str | None,
    behind_points: int | None,
) -> str:
    is_close = behind_points is not None and behind_points < 50

    if is_first:
        text = get_random_message("first", behind_nickname, behind_points)
    elif is_podium and is_close:
        text = get_random_message("close_podium", behind_nickname, behind_points)
    elif is_podium:
        text = get_random_message("podium", behind_nickname, behind_points)
    elif is_last:
        text = get_random_message("last", behind_nickname, behind_points)
    elif is_close:
        text = get_random_message("close_regular", behind_nickname, behind_points)
    else:
        text = get_random_message("regular", behind_nickname, behind_points)

    return text
