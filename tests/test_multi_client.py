# TEST MULTIPLE CLIENTS
# Tests the Quiz Master server against multiple clients at once
import socket
import threading
import time

# Should remain unchanged if running on same device as server
HOST = "127.0.0.1"
PORT = 7878

# Number of clients to create and connect
CLIENTS = 50


def client_worker(client_id: str) -> None:
    message = (
        f'{{"type": "join_lobby", "data": {{"nickname": "{client_id}"}}}}\n'
    ).encode()

    # Establish connection
    client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    client.connect((HOST, PORT))

    print(f"Client {client_id} connected")

    client.sendall(message)

    # Keep listening while the client is alive
    client.settimeout(1.0)

    while True:
        try:
            data = client.recv(4096)
        except TimeoutError:
            # No message yet; keep client alive
            continue

        if not data:
            print(f"Client {client_id} disconnected :(")
            break

        print(f"Client {client_id} response: {data.decode()}")


def main() -> None:
    threads = []

    # Use threading to make all clients connect simultaneously
    for i in range(CLIENTS):
        client_id = str(i).zfill(len(str(CLIENTS)))
        thread = threading.Thread(target=client_worker, args=(client_id,), daemon=True)

        threads.append(thread)
        thread.start()

        time.sleep(0.01)

    print(f"{CLIENTS} clients started")

    # Keep the test running
    try:
        while True:
            time.sleep(1)
    except KeyboardInterrupt:
        print("Stopping clients...")


if __name__ == "__main__":
    main()
