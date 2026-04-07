import json
from socket import socket


def send(sock: socket, data: dict) -> None:
    """
    Send data from the sender to the receiver as JSON.

    Parameters:
        sock (socket): The socket to send from. For example, if the client wishes to send data to the server, the socket should be the instance of the client, not the server.
        data (dict): The data to send, as a dictionary. The data will be serialized before being sent.
    """

    msg = json.dumps(data) + "\n"
    sock.sendall(msg.encode())


def recv(sock: socket) -> dict:
    """
    Receive data from the sender as a Python dictionary.

    Parameters:
        sock (socket): The socket to receive data from. For example, if the client expects data from the server, the socket should be the instance of the client, not the server.

    Returns:
        dict: A dictionary of the data received. The data will be deserialized before being returned.
    """

    # TODO apparently this implmentation can rarely break
    # this may need to be OOP-based
    buffer = ""

    # While the end-of-stream is not received, continue receiving
    while "\n" not in buffer:
        chunk = sock.recv(4096).decode()
        if not chunk:
            return None

        buffer += chunk

    # Remove newline delimiter and parse JSON
    line, _, buffer = buffer.partition("\n")
    return json.loads(line)
