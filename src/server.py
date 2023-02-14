"""CD Chat server program."""
import logging
#imports que acrescentei 
import socket
import selectors

logging.basicConfig(filename="server.log", level=logging.DEBUG)

sel = selectors.DefaultSelector()

class Server:
    """Chat Server process."""
    
    def loop(self):
        """Loop indefinetely."""

    def accept(sock, mask):
        conn, addr = sock.accept()  # Should be ready
        print('accepted', conn, 'from', addr)
        conn.setblocking(False)
        sel.register(conn, selectors.EVENT_READ, read)

    def read(conn, mask):
        data = conn.recv(1000)  # Should be ready
        if data:
            print('echoing', repr(data), 'to', conn)
            conn.send(data)  # Hope it won't block
        else:
            print('closing', conn)
            sel.unregister(conn)
            conn.close()

    sock = socket.socket()
    sock.bind(('localhost', 1234))
    sock.listen(100)
    sock.setblocking(False)
    sel.register(sock, selectors.EVENT_READ, accept)

    while True:
        events = sel.select()
        for key, mask in events:
            callback = key.data
            callback(key.fileobj, mask)





