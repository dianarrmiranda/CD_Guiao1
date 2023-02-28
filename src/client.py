"""CD Chat client program"""
import logging
import selectors
import socket
import sys

from .protocol import CDProto, CDProtoBadFormat

logging.basicConfig(filename=f"{sys.argv[0]}.log", level=logging.DEBUG)


class Client:
    """Chat Client process."""

    def __init__(self, name: str = "Foo"):
        """Initializes chat client."""
        self.name = name
        self.socket = None
        self.sel = selectors.DefaultSelector()
        self.connected = False
        pass

    def connect(self):
        """Connect to chat server and setup stdin flags."""
        self.socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.socket.connect(("localhost", 5000))
        self.socket.setblocking(False)
        self.connected = True;
        self.sel.register(self.socket, selectors.EVENT_READ, data=None)
        pass


    def loop(self):
        """Loop indefinetely."""
        while self.connected:
            # Check for input from the user
            try:
                message = input()
                if message.startswith("/join "):
                    channel = message[6:]
                    self.protocol.change_channel(channel)
                elif message == "exit":
                    self.protocol.disconnect()
                    self.connected = False
                else:
                    self.protocol.send_message(message)
            except EOFError:
                # End of input stream, terminate the client
                self.protocol.disconnect()
                self.connected = False
            except CDProtoBadFormat as e:
                logging.error(e)
            except Exception as e:
                logging.exception(e)