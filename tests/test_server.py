# TEST SERVER
# Tests the Quiz Master client against a bad server.
import socket

# Should remain unchanged
HOST = "127.0.0.1"
PORT = 7878

# Message to send to the client after it connects
MESSAGE = b"" + b"\n"


def main() -> None:
    # Start server
    server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server.bind((HOST, PORT))

    server.listen(1)

    print(f"Waiting for client on {HOST}:{PORT}...")

    # Wait for Quiz Master client to connect
    client, address = server.accept()
    print("Client connected:", address)

    # Send message to the client
    client.sendall(MESSAGE)

    client.settimeout(1.0)

    # Get responses from client
    while True:
        try:
            data = client.recv(4096).decode()
        except TimeoutError:
            continue

        if not data:
            print("Client disconnected :(")
            break

        print("Response:", data)

    client.close()
    server.close()


if __name__ == "__main__":
    main()
