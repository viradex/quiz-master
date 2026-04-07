class CommonUI:
    """Base class for managing UI elements."""

    @staticmethod
    def player_joined(nickname: str) -> None:
        if not nickname:
            raise ValueError("Nickname must not be empty")

        print(f"{nickname} joined the game\n")

    @staticmethod
    def player_left(nickname: str) -> None:
        if not nickname:
            raise ValueError("Nickname must not be empty")

        print(f"{nickname} left the game\n")

    @staticmethod
    def player_kicked(name: str) -> None:
        print(f"Player {name} was kicked from the server\n")

    @staticmethod
    def cli_start(type: str) -> None:
        print(f"Basic {type.lower()} command-line interpreter (type 'help' for help)")

    @staticmethod
    def show_players(players: list) -> None:
        """Show all users currently connected to the server."""
        if len(players) == 0:
            print("No players are currently connected")
        else:
            print("\nPlayers:")
            for name in players:
                print(f"- {name}")

        print()

    @staticmethod
    def show_scores(scores: dict) -> None:
        """Show all players and their respective final scores."""
        print("\nFinal scores:")
        sorted_scores = sorted(scores.items(), key=lambda x: x[1], reverse=True)

        for name, score in sorted_scores:
            print(f"{name}: {score}")

        print()

    @staticmethod
    def show_question(num: int, question: str, choices: list[str]) -> None:
        """Show question and available answers."""
        whitespace = " " * (len(str(num)) + 2)
        letters = ["a", "b", "c", "d"]

        if len(choices) > 4:
            raise ValueError("Too many choices, max 4")

        print(f"\n{num}) {question}")
        for i, choice in enumerate(choices):
            print(f"{whitespace}{letters[i]}. {choice}")

        print()
