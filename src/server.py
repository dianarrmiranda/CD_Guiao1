"""CD Chat server program."""
import json
import logging
import select
import selectors
import socket

logging.basicConfig(filename="server.log", level=logging.DEBUG)


class Server:
    """Chat Server process."""

    def __init__(self, host: str = "localhost", port: int = 5000):
        """Initializes chat server."""
        self.host = host
        self.port = port
        self.channels = {}
        self.sel = selectors.DefaultSelector()
        self.sock = socket.socket()
        self.sock.bind((host, port))
        self.sock.listen(100)

    def accept(self, sock, mask):
        conn, addr = sock.accept()  # Should be ready
        logging.debug(f"Accepted connection from {addr}")
        conn.setblocking(False)
        self.sel.register(conn, selectors.EVENT_READ, self.read)

    def read(self, conn, mask):
        data = conn.recv(1024)  # Should be ready
        if data:
            logging.debug(f"Received message: {message}")
            message = json.loads(data.decode())

            if message.get("command") == "/join":
                channel_name = message.get("channel")
                if channel_name not in self.channels:
                    self.channels[channel_name] = []
                self.channels[channel_name].append(conn)
                logging.debug(f"Added connection to channel {channel_name}")
            elif message.get("command") == "exit":
                self.sel.unregister(conn)
                conn.close()
                logging.debug(f"Closed connection")
            else:
                channel_name = message.get("channel")
                if channel_name in self.channels:
                    for c in self.channels[channel_name]:
                        if c != conn:
                            c.send(data)
        else:
            self.sel.unregister(conn)
            conn.close()
            logging.debug(f"Closed connection")

    def loop(self):
        """Loop indefinetely."""
        self.sel.register(self.sock, selectors.EVENT_READ, self.accept)
        while True:
            events = self.sel.select()
            for key, mask in events:
                callback = key.data
                callback(key.fileobj, mask)
