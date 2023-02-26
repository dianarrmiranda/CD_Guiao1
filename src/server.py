"""CD Chat server program."""
import logging
#imports que acrescentei 
import socket
import selectors
import json

logging.basicConfig(filename="server.log", level=logging.DEBUG)

class Server:
    """Chat Server process."""

    def __init__(self, host: str = "localhost", port: int = 1234):
        """Initializes chat server."""
        self.host = 'localhost'
        self.port = 1234
        self.sel = selectors.DefaultSelector()
        self.channels = {}

    
    def loop(self):
        """Loop indefinetely."""
        self.sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.sock.bind((self.host, self.port))
        self.sock.listen()
        logging.debug(f"Listening on {self.host}:{self.port}")
        self.sel.register(self.sock, selectors.EVENT_READ, data=None)

        while True:
            events = self.sel.select()
            for key, mask in events:
                if key.data is None:
                    self.accept(key.fileobj, mask)
                else:
                    self.read(key.fileobj, mask)

    def accept(self, sock, mask):
        conn, addr = sock.accept()
        logging.debug(f"Accepted connection from {addr}")
        conn.setblocking(False)
        self.sel.register(conn, selectors.EVENT_READ, data={})

    def read(self, conn, mask):
        data = conn.recv(1024)
        if data:
            message = json.loads(data.decode())
            logging.debug(f"Received message: {message}")

            if message.get("command") == "/join":
                channel_name = message.get("channel")
                if channel_name not in self.channels:
                    self.channels[channel_name] = []
                self.channels[channel_name].append(conn)
                logging.debug(f"Added connection to channel {channel_name}")
            elif message.get("command") == "/exit":
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






