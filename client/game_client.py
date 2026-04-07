import socket
import sys
import threading

from common.protocol import send, recv
from common.messages import MessageType
from client.client_ui import ClientUI


class GameClient:
    """This class manages the client: initializing it, joining the server, and displaying information to the user and allowing them to communicate with the server."""

    def __init__(self, port):
        """
        Initialize the client. This does not connect to the server.

        Parameters:
            port (int): The port to try to connect to on the IP address. Set this to the same port as the server.
        """

        self.port = port
        self.host: str = None

        self.nickname: str = None
        self.client: socket.socket = None

        self.in_game = False
        self.answered = False
        self.awaiting_player_list = False

    def get_ip_address(self) -> None:
        """Prompt user for IP address to connect to."""
        self.host = ClientUI.get_ip_address()

    def get_nickname(self) -> None:
        """Prompt user for nickname to join as."""
        self.nickname = ClientUI.get_nickname()

    def connect(self):
        """Connect to the server on the specified host and port, and start the client CLI. Starts listening for messages from the server."""
        if self.host is None or self.nickname is None:
            raise ValueError(
                "host and nickname must have values, call get_ip_address() and get_nickname() before connecting"
            )

        try:
            self.client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            self.client.connect((self.host, self.port))
        except ConnectionRefusedError:
            # If the server has not started
            print(
                f"\nThe server could not be found (tried connecting to {self.host}:{self.port} but the connection was refused).\n"
            )
            sys.exit(1)

        ClientUI.join_server(self.host, self.port)
        self.send_join()

        ClientUI.cli_start("client")
        threading.Thread(target=self.client_input_loop, daemon=True).start()

        self.listen()

    def client_input_loop(self) -> None:
        """Run the client CLI prompt."""
        while True:
            try:
                cmd = input("> ").strip()
            except EOFError:
                break

            if not cmd:
                continue

            self.handle_client_command(cmd)

    def listen(self) -> None:
        """Listens for any incoming messages from the server. Only accepts serialized JSON data."""
        while True:
            msg = recv(self.client)

            if msg is None:
                break

            self.handle_message(msg)

    def handle_client_command(self, cmd: str) -> None:
        """
        Parse and evaluate a command entered into the client CLI, calling the respective function
        for the specified command.

        Parameters:
            cmd (str): The full command entered, including arguments.
        """
        command, arg = ClientUI.parse_command(cmd)

        if command == "help":
            ClientUI.show_help()

        elif command == "list":
            self.ask_player_list()

        elif command == "answer":
            self.send_answer(arg)

        elif command == "quit":
            self.leave_server()

        elif command == "error":
            # Handle errors such as the absense of arguments
            print(arg + "\n")

        else:
            print("Invalid command. Type 'help' for available commands\n")

    def handle_message(self, msg) -> None:
        """
        Handle messages from the server appropriately by matching the `type` key in the dictionary
        from the message to any valid value in `MessageType`.

        Parameters:
            msg (dict): A dictionary containing the data that the server sent. Must include the `type` key.
        """
        msg_type = msg["type"]

        if msg_type == MessageType.OTHER_JOIN:
            self.handle_other_join(msg)
        elif msg_type == MessageType.KICK:
            self.handle_kick(msg)
        elif msg_type == MessageType.OTHER_KICK:
            self.handle_other_kick(msg)
        elif msg_type == MessageType.OTHER_LEAVE:
            self.handle_other_leave(msg)
        elif msg_type == MessageType.PLAYER_LIST:
            self.handle_player_list(msg)
        elif msg_type == MessageType.SHUT_DOWN:
            self.handle_shut_down(msg)
        elif msg_type == MessageType.STARTING:
            self.handle_starting(msg)
        elif msg_type == MessageType.QUESTION:
            self.handle_question(msg)
        elif msg_type == MessageType.ANSWER_RESULT:
            self.handle_answer_result(msg)
        elif msg_type == MessageType.GAME_OVER:
            self.handle_game_over(msg)
        else:
            raise ValueError(
                f"The message type {msg_type} did not match any expected types"
            )

    def handle_other_join(self, msg: dict) -> None:
        """Handles an `OTHER_JOIN` message type. Prints the new user's nickname."""
        ClientUI.player_joined(msg["nickname"])

    def handle_kick(self, msg: dict) -> None:
        """Handles a `KICK` message type. Prints the reason for the kick."""
        ClientUI.connection_lost(msg["reason"])

    def handle_other_kick(self, msg: dict) -> None:
        """Handles an `OTHER_KICK` message type. Prints the user who was kicked's nickname."""
        ClientUI.player_kicked(msg["nickname"])

    def handle_other_leave(self, msg: dict) -> None:
        """Handles an `OTHER_LEAVE` message type. Prints the user's nickname. Ignored if the nickname is the same as current user."""
        if msg["nickname"] != self.nickname:
            ClientUI.player_left(msg["nickname"])

    def handle_player_list(self, msg: dict) -> None:
        """Handles a `PLAYER_LIST` message type. If the user ran `list`, shows players as delivered from the server."""
        if self.awaiting_player_list:
            ClientUI.show_players(msg["players"])

        self.awaiting_player_list = False

    def handle_shut_down(self, msg: dict) -> None:
        """Handles a `SHUT_DOWN` message type. Informs the user that the server shut down."""
        ClientUI.connection_lost(msg["reason"])

    def handle_starting(self, msg: dict) -> None:
        """Handles a `STARTING` message type. Informs the user that the game about to start, and sets the `in_game` flag to true."""
        print("Starting game...\n")
        self.in_game = True

    def handle_question(self, msg: dict) -> None:
        """Handles a `QUESTION` message type. Prints the question and becomes ready for the user's answer."""
        if self.in_game:
            self.answered = False
            ClientUI.show_question(msg["number"], msg["question"], msg["choices"])

    def handle_answer_result(self, msg: dict) -> None:
        """Handles an `ANSWER_RESULT` message type. Informs the user whether they got the previous question right or not."""
        if msg["result"] == "correct":
            print("You got it right!\n")
        else:
            letters = ("A", "B", "C", "D")
            print(f"Wrong! The correct answer was {letters[msg["correct_index"]]}\n")

    def handle_game_over(self, msg: dict) -> None:
        """Handles a `GAME_OVER` message type. Shows all players' scores."""
        self.in_game = False
        ClientUI.show_scores(msg["scores"])

    def send_answer(self, answer: str) -> None:
        """
        Send the inputed answer to a question to the server, and prevents
        overwriting that answer until the next question.

        This method runs when running the `answer` command. The command only
        works when the game has started, the answer hasn't been submitted yet,
        or the answer is valid.

        Parameters:
            answer (str): The answer the user selected (anything from a-d).
        """

        if not self.in_game:
            print("This command can only be run once the game has started\n")
            return

        elif self.answered:
            print("You already answered\n")
            return

        valid_answers = ["a", "b", "c", "d"]
        answer = answer.lower().strip()

        if answer not in valid_answers:
            print("Invalid answer\n")
            return

        send(
            self.client,
            {"type": MessageType.ANSWER, "answer": valid_answers.index(answer)},
        )
        self.answered = True

        print("Answered!\n")

    def ask_player_list(self) -> None:
        """Runs when the `list` command is entered. Requests the server for the player list. Once received, the method `handle_player_list()` prints it."""
        self.awaiting_player_list = True
        send(self.client, {"type": MessageType.PLAYER_LIST})

    def send_join(self) -> None:
        """Inform the server that this client has joined the server formally, with the specified nickname."""
        send(self.client, {"type": MessageType.JOIN, "nickname": self.nickname})

    def leave_server(self) -> None:
        """Inform the server that this client has left the server. Once done, stops this client process."""
        send(self.client, {"type": MessageType.LEAVE, "nickname": self.nickname})

        ClientUI.player_left(self.nickname)
        sys.exit(0)
