import json


class JSONSocket:
    def __init__(self, sock=None):
        self.sock = sock
        self.buffer = b""

    def _validate_socket(self):
        if self.sock is None:
            raise ValueError("Socket must be set before sending/receiving")

    def send(self, data):
        self._validate_socket()

        msg = json.dumps(data) + "\n"
        self.sock.sendall(msg.encode())

    def recv(self):
        self._validate_socket()

        while b"\n" not in self.buffer:
            try:
                chunk = self.sock.recv(4096)
            except OSError:
                return None

            if not chunk:
                return None

            self.buffer += chunk

        line, self.buffer = self.buffer.split(b"\n", 1)

        try:
            return json.loads(line.decode())
        except json.JSONDecodeError:
            self.buffer = b""
            return None

    def set_socket(self, sock):
        self.sock = sock
