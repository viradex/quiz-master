"""
transport.py

Contains the transport sending and receiving functions for the server and client, central to
networking communication.
"""

import json
import socket

from core.config.constants import MAX_MESSAGE_SIZE


class JSONSocket:
    """
    A low-level abstraction for sending bytes across a TCP stream between the server and client. Instead
    of sending/receiving raw bytes, JSONSocket allows sending Python dictionaries across the network by
    automatically serializing the dictionary into JSON, and then sending it. It also allows listening to
    messages and deserializing the data when a full JSON object is received, to convert it into a Python
    dictionary.

    This class does not create a network connection itself; it wraps an existing socket.

    Arguments:
        sock: The socket connection to use on behalf of sending/receiving messages, or None. If set to
            None (which is done by default), the value must be set before sending/receiving messages
            using `set_socket()`.
    """

    def __init__(self, sock: socket.socket | None = None) -> None:
        self.sock = sock

        # TCP arrives as a stream, so save data in buffer (as bytes)
        self.buffer = b""

    def send(self, data: dict) -> None:
        """
        Sends a Python dictionary to the receiving end. The dictionary is serialized into JSON before being
        encoded and sent.

        Arguments:
            data: The dictionary containing the data to send to the receiving end. A dictionary is used as
                it can store multiple values in one variable and can be easily serialized into JSON.

        Returns:
            None.

        Raises:
            RuntimeError: If the socket was not set before running this method.

            ValueError: If the data provided could not be serialized into JSON, or if the data could not be
                encoded using UTF-8 encoding.
        """
        if self.sock is None:
            raise RuntimeError("Socket must be set before sending data")

        try:
            # Add newline delimiter to signify separator for receiving end, since
            # TCP does not preserve message boundaries.
            msg = json.dumps(data) + "\n"
        except (TypeError, ValueError) as e:
            raise ValueError("Invalid dictionary data") from e

        try:
            # Encodes the string into UTF-8 bytes and sends all data
            self.sock.sendall(msg.encode())
        except UnicodeEncodeError as e:
            raise ValueError("Invalid UTF-8 data") from e

    def recv(self) -> dict | bool | None:
        """
        When called, checks if any messages have been sent to this device. If so, it keeps reading the data
        that was received until encountering a delimiter, which signifies the end of a message, and saves it
        to the buffer. The message is then exclusively deserialized into a Python dictionary and then returned.

        If multiple messages were received at once, the second message is stored in the buffer until retrieved
        by another `recv()` call. If the buffer size exceeds the maximum message size, the method stops reading
        further messages prematurely to protect the device from excessive memory usage, in case of a malicious
        sender.

        Returns:
            A dictionary containing the deserialized data that was transferred across the network if the entire
            receiving process was successful. Otherwise, False is returned if the process timed out, but the
            other end is still alive. None is returned if the other end has closed its connection and messages
            cannot be received from them anymore.

        Raises:
            RuntimeError: If the socket was not set before running this method.

            ValueError: If the buffer exceeds the maximum message size allowed. Also, if the data could not be
                decoded from UTF-8 encoding, or if it could not be deserialized from JSON.

            TypeError: If the message received was not a JSON object and did not convert into a Python dictionary.
        """
        if self.sock is None:
            raise RuntimeError("Socket must be set before receiving data")

        # Keeps reading until reaching end of message (newline delimiter),
        # since TCP doesn't have message boundaries.
        while b"\n" not in self.buffer:
            try:
                # Reads up to 4096 bytes at a time
                chunk = self.sock.recv(4096)
            except TimeoutError:
                # Other end hasn't sent anything yet, but connection is still alive
                return False
            except OSError:
                # Socket errors are treated as a dead connection
                return None

            # Connection closed
            if not chunk:
                return None

            self.buffer += chunk

            # Protects device against huge messages from malicious senders,
            # which can cause extreme memory usage.
            if len(self.buffer) > MAX_MESSAGE_SIZE:
                raise ValueError("Message too large")

        # Extracts first complete message from buffer, and saves remaining data for next recv() call
        line, self.buffer = self.buffer.split(b"\n", 1)

        try:
            # Decode into a string and convert to dictionary
            data = json.loads(line.decode())
        except UnicodeDecodeError as e:
            raise ValueError("Invalid UTF-8 data") from e
        except json.JSONDecodeError as e:
            raise ValueError("Invalid JSON data") from e

        # Ensure it is a dictionary and not some other valid JSON value, like a list (array)
        if not isinstance(data, dict):
            raise TypeError("Message must be a JSON object")

        return data

    def set_socket(self, sock: socket.socket) -> None:
        """
        Set the socket for this class to use to send and receive messages on.

        Arguments:
            sock: The socket connection to use on behalf of sending/receiving messages.

        Returns:
            None.
        """
        self.sock = sock
