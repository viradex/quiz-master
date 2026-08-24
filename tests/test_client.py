# TEST CLIENT
# Tests the Quiz Master server against bad clients.
import socket

# Should remain unchanged if running on same device as server
HOST = "127.0.0.1"
PORT = 7878

# CUSTOMIZE THE FIRST STRING to send a certain invalid message to the server upon connecting
MESSAGE = b"" + b"\n"

# The number of times to send the message above
REPEATS = 1


def main() -> None:
    # Establish connection
    client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    client.connect((HOST, PORT))

    # Allows KeyboardInterrupts to go through
    client.settimeout(1.0)

    for i in range(REPEATS):
        client.sendall(MESSAGE)

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
