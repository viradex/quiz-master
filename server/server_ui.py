from common.common_ui import CommonUI


class ServerUI(CommonUI):
    """Class for managing server UI elements."""

    @staticmethod
    def start_server(host: str, port: str | int, ip: str) -> None:
        print(f"\nStarted server, listening on {host} on port {port}")
        print(f"Clients can join by connecting to: {ip}\n")

    @staticmethod
    def client_connected(ip: str, port: str | int) -> None:
        print(f"Client joined (IP {ip}:{port})")

    @staticmethod
    def server_shutdown() -> None:
        print("Server has been shut down\n")

    @staticmethod
    def parse_command(cmd) -> tuple[str, str | None]:
        """Parse a full command entered by the user into the actual command and arguments, if any."""
        parts = cmd.split()
        command = parts[0]

        if command == "help":
            return ("help", None)

        elif command == "start":
            return ("start", None)

        elif command == "list":
            return ("list", None)

        elif command == "kick":
            if len(parts) < 2:
                return ("error", "Name must be provided")
            return ("kick", parts[1])

        elif command == "stop":
            return ("stop", None)

        else:
            return ("invalid", None)

    @staticmethod
    def show_help() -> None:
        help_messages = {
            "start": "Start the game",
            "list": "List all nicknames of players currently on the server",
            "kick <name>": "Kick the specified player from the server",
            "stop": "Shut down the server",
            "help": "Show this menu",
        }

        for help_cmd in help_messages:
            print(f"{help_cmd} - {help_messages[help_cmd]}")

        print()
