"""CD Chat server program."""

import logging
import selectors
import socket
from .protocol import CDProto

logging.basicConfig(filename="server.log", level=logging.DEBUG)


class Server:
    """Chat Server process."""

    def __init__(self):
        """Initializes chat server."""
        self.host = "localhost"
        self.port = 5000

        self.sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM) #para não bloquear o socket
        self.sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        self.sock.bind((self.host, self.port))
        self.sock.listen(100)

        self.sel = selectors.DefaultSelector()
        self.sel.register(self.sock, selectors.EVENT_READ, self.accept)
        
        self.channels = {"all": []}

    def loop(self):
        """Loop indefinetely."""
        while True:
            events = self.sel.select()
            for key, mask in events:
                callback = key.data
                callback(key.fileobj)

    def accept(self, sock):
        conn, addr = sock.accept() 
        logging.debug('Accepted connection from %s ', addr)
        self.sel.register(conn, selectors.EVENT_READ, self.read)

    def read(self, conn):
        message = CDProto.recv_msg(conn)  # recebe a mensagem
        logging.debug('Accepted message %s ', message)
        #print("m: " + str(message))

        if message:
            if message.command == "register":
                #print("Add User " + message.user)
                self.channels["all"].append(conn)
            elif message.command == "join":
                #print("Join to channel " + message.channel)
                if message.channel not in self.channels:
                    self.channels[message.channel] = []
                self.channels[message.channel].append(conn)
            elif message.command == "message":
                #print("Send message to " + str(message.channel))
                if message.channel is None: message.channel = "all"
                for c in self.channels[message.channel]:
                    if c != conn:
                        CDProto.send_msg(c, message)
            else:
                logging.error('Unknown command %s ', message.command)
            return
        else:
            logging.debug('Closing connection to %s ', conn)
            for channel in self.channels:
                if conn in self.channels[channel]:
                    self.channels[channel].remove(conn)
                
            self.sel.unregister(conn)
            conn.close()

