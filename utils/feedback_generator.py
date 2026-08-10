"""
feedback_generator.py

Generates feedback depending on the place that the player came at, among other conditions, giving
a personalized feedback that is (mostly) unique every game.
"""

import random

# Feedback messages definition, with weighting % respective to the string at the same index.
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
    """
    Generate personalized feedback messages based on certain conditions.

    Arguments:
        is_podium: Whether or not the player is on the podium. A boolean is used as it is naturally a
            yes/no-style value.

        is_first: Whether or not the player is in first place. A boolean is used as it is naturally a
            yes/no-style value.

        is_last: Whether or not the player is in last place. A boolean is used as it is naturally a
            yes/no-style value.

        behind_nickname: The nickname of the player the current player is behind, or None if the player
            is first place. A string is used as a nickname is easily represented by a string.

        behind_points: The number of points the current player is behind the player in front, or None
            if the player is first place. An integer is used as the number of points is typically a whole
            number.

    Returns:
        The string of the personalized feedback message. A string is used as strings naturally represent
        sentences.
    """
    # Generate boolean conditions derived from the number of points behind
    is_close = behind_points is not None and behind_points < 50
    is_tie = behind_points is not None and behind_points == 0

    # Decide the key depending on conditions
    if is_first:
        key = "first"
    elif is_podium and is_tie:
        key = "tie_podium"
    elif is_podium and is_close:
        key = "close_podium"
    elif is_podium:
        key = "podium"
    elif is_last:
        key = "last"
    elif is_tie:
        key = "tie_regular"
    elif is_close:
        key = "close_regular"
    else:
        key = "regular"

    return _get_random_message(key, behind_nickname, behind_points)


def _get_random_message(message_type: str, nickname: str, points: str | int) -> str:
    """
    Internal function. Chooses a random message from the MESSAGES constant, and chooses a random message
    from the pool of messages depending on the message type, considering weighting. The string has its
    nickname and points replaced, if necessary.

    Arguments:
        message_type: A string that represents the type of message pool to search in. This must be a
            valid key in the MESSAGES constant.

        nickname: The nickname of the player in front of the current player. A string is used as a nickname
            is easily represented by a string.

        points: The number of points the current player is behind the player in front. An integer is used
            as the number of points is typically a whole number and naturally an integer, but a string is
            also accepted, as the integer is inevitably converted to a string when formatted.
    """
    messages, weights = MESSAGES[message_type]

    # The choices() function always returns a list, even if k=1, therefore get
    # first element. Then, replace all instances of {nickname} and {points} with
    # their actual values, if required.
    return random.choices(messages, weights=weights)[0].format(
        nickname=nickname, points=points
    )
