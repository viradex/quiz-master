# TEST CLIENT DELAY
# Tests the Quiz Master server against bad clients, with a bad message during the server lifecycle.
import socket

# Should remain unchanged if running on same device as server
HOST = "127.0.0.1"
PORT = 7878

MESSAGE_ONE = b'{"type": "join_lobby", "data": {"nickname": "TEST CLIENT"}}' + b"\n"
MESSAGE_TWO = b'{"type": "answer_submit", "data": {"selected_index": -1}}' + b"\n"


def main() -> None:
    # Establish connection
    client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    client.connect((HOST, PORT))

    # Allows KeyboardInterrupts to go through
    client.settimeout(1.0)

    client.sendall(MESSAGE_ONE)

    # Wait for you to press Enter
    input("Press Enter to send the ANSWER_SUBMIT message...")
    client.sendall(MESSAGE_TWO)

    # Get responses from server
    while True:
        try:
            data = client.recv(4096).decode()
        except TimeoutError:
            continue

        if not data:
            print("Client disconnected :(")
            break

        print("Response:", data)


if __name__ == "__main__":
    main()
