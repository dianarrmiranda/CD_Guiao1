"""CD Chat client program"""
import logging
import sys
import socket
import selectors

from .protocol import CDProto, CDProtoBadFormat


logging.basicConfig(filename=f"{sys.argv[0]}.log", level=logging.DEBUG)


class Client:
    """Chat Client process."""

    def __init__(self, name: str = "Foo"):
        """Initializes chat client."""
        self.name = name
        self.socket = None
        self.sel = selectors.DefaultSelector()
        pass

    def connect(self):
        """Connect to chat server and setup stdin flags."""
        self.socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.socket.connect(("localhost", 1234))
        self.socket.setblocking(False)

        self.sel.register(self.socket, selectors.EVENT_READ, data=None)
        pass

    def loop(self):
        """Loop indefinetely."""
        while True:
            events = self.sel.select()
            for key, mask in events:
                if key.data is None:
                    message = input("> ")
                    if message == "/exit":
                        self.socket.close()
                        sys.exit()
                    elif message.strartswith("/join"):
                        channel = message.split()[1]
                        msg = CDProto.join(self.name, channel)
                        self.socket.sendall(msg.encode())
                    else:
                        msg = CDProto.send(self.name, message)
                        self.socket.sendall(msg.encode())
                else:
                    data = key.fileobj.recv(1024)
                    if not data:
                        self.sel.unregister(key.fileobj)
                        self.socket.close()
                        sys.exit()
                    else:
                        try:
                            msg = CDProto.decode(data)
                            logging.debug(f"Received message: {msg}")
                            print(f"{msg['from']}: {msg['message']}")
                        except CDProtoBadFormat as e:
                            logging.error(str(e))
                            print(f"Error: {e}")
        pass
