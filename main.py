from server.game_server import GameServer
from client.game_client import GameClient
from utils.json_loader import JSONLoader

SERVER_IP = "0.0.0.0"
PORT = 5555


def host_game() -> None:
    """Start the server for hosting the game and handling clients."""

    questions = JSONLoader().load_all()
    server = GameServer(SERVER_IP, PORT, questions)

    # TODO in GameServer init?
    server.start()
    server.accept_clients()


def join_game() -> None:
    """Start the program as a client to join a server."""

    client = GameClient(PORT)

    # TODO in GameClient init?
    client.get_ip_address()
    client.get_nickname()
    client.connect()


def main() -> None:
    """Start the program with a prompt to ask whether to start the program as a server or client."""

    print("Would you like to...\n1. Host game\n2. Join game\n")
    while True:
        choice = input("Enter choice (or blank to exit): ").strip()

        if choice == "1":
            host_game()
        elif choice == "2":
            join_game()
        elif choice == "":
            print("Exiting...")
        else:
            print("Invalid choice\n")
            continue

        break


if __name__ == "__main__":
    main()
