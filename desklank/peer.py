from lank.peer import (get_handler, HELLO_TIMEOUT, GENERAL_TIMEOUT, HELLO,
                       HELLO_SIZE)
from lank.peer.protocol.v2 import *

from threading import Thread, Event
from queue import Queue, Empty
import socket


KEEPALIVE = 90 #FIXME


class Server(Thread):
    def __init__(self, app, label, port, verbose=True):
        super().__init__(name='peer-server')
        self.app = app
        self.verbose = verbose

        self.label = label
        self.port = port
        self.crypto = None #FIXME
        self.priv_key = None #FIXME

        self.sock = None
        self.peers = { }
        self.buffer = bytearray(HELLO_SIZE)
        self.ready = Event()

    def run(self):
        addr = ('', self.port)
        self.print(f'listening at {addr}')

        try:
            self.sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            self.sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
            self.sock.bind(addr)
            self.sock.listen(5)
            self.ready.set()

            while self.sock:
                client, addr = self.sock.accept()
                self.handle(client, addr)

        except ConnectionRefusedError:
            self.error('[REFUSED]', True)

        except socket.timeout:
            self.error('[TIMEOUT]', True)

        except OSError as e:
            self.error(f'[CLOSED] {e}')

        finally:
            self.sock = None
            self.print('peer server exiting')

            for thread in self.peers.values():
                thread.join()

            self.ready.set()
            self.print('peer server finished')

    def handle(self, sock, addr):
        self.print(f' + connection from {addr}')
        sock.settimeout(HELLO_TIMEOUT)

        try:
            read = sock.recv_into(self.buffer)

            if read == HELLO_SIZE:
                if self.buffer == HELLO:
                    sock.settimeout(GENERAL_TIMEOUT)

                    try:
                        #self.print('getting protocol handler')
                        protocol = get_handler(sock, addr,
                            self.crypto, self.priv_key)

                        if protocol:
                            #self.print('got handler')
                            protocol.print = self.print
                            try:
                                def server():
                                    try:
                                        #self.print('running server')
                                        protocol.server(self)
                                    except Exception as e:
                                        self.error(e)
                                    finally:
                                        self.print(f' - finished {addr}')
                                        #del self.peers[protocol]

                                thread = Thread(
                                    name='peer-server-client',
                                    target=server)

                                self.peers[protocol] = thread
                                thread.start()

                            except BrokenPipeError:
                                self.error(f' - closed {addr} [BROKEN PIPE]',
                                    True, False)

                            except ValueError as e:
                                self.error(f' - terminated {addr}' \
                                    + f' [BAD MESSAGE: {e}]', True)

                        else:
                            self.error(f' - closed {addr} [CLIENT ABORT]', True,
                                False)

                    except ValueError as e:
                        self.error(f' - terminated {addr} [PROTOCOL VERSION]',
                            True, False)

                    except timeout:
                        self.error(f' - terminated {addr} [GENERAL TIMEOUT]',
                            True, False)

                else:
                    self.error(f' - terminated {addr} [BAD HELLO]', True, False)

            elif read:
                self.error(f' - terminated {addr} [BAD HELLO]', True, False)

            else:
                self.error(f' - closed {addr} [CLIENT ABORT]', True, False)

        except socket.timeout:
            self.error(f' - terminated {addr} [HELLO TIMEOUT]', True, False)

    def on_peered(self, handler):
        from .page.peer import Module as Peer
        from .page.connection import Module as Connection

        label = handler.label
        addr = handler.addr
        #pub_key = handler.pub_key

        self.app._notify_(label, f'new connection from {label} {addr}')
        peer = None

        for mod in self.app.desk._menu:
            if isinstance(mod, Peer):
                if mod.label == label:
                    peer = mod
                    break

        if not peer:
            peer = Peer(self.app.desk, label)
            self.app.desk.logic.setup_panel(peer)

        mod = Connection(self.app.desk, peer, label, '', f'{addr[0]}:{addr[1]}',
            handler)
        self.app.desk.logic.setup_panel(mod)

        # FIXME hack:
        idx = self.app.desk._menu.index(peer)
        if self.app.desk._menu.index(mod) != idx+1:
            del self.app.desk._menu[self.app.desk._menu.index(mod)]
            self.app.desk._menu.insert(idx+1, mod)
            oldpanels = self.app.desk.logic.available_panels
            newpanels = { mod.name: oldpanels[mod.name]
                            for mod in self.app.desk._menu }
            self.app.desk.logic.available_panels = newpanels

    def on_text(self, msg, handler):
        self.print(f'server got text: {msg}')

    def stop(self):
        if not self.sock: return
        sock = self.sock
        self.sock = None

        sock.shutdown(socket.SHUT_RDWR)
        sock.close()
        #self.output.put_nowait(None)
        #self.input.put_nowait(None)

        for handler in self.peers:
            handler.sock.shutdown(socket.SHUT_RDWR)
            handler.sock.close()

        self.ready.set()

    def get_public_key(self, crypto, label):
        if not self.app.node:
            return None

        queue = Queue(maxsize=1)

        def on_registration(msg):
            queue.put_nowait(msg)

        self.app.node.get_registration(label, on_registration)
        msg = queue.get()

        return crypto.load_public_key(msg.key_pair_pem)

    def print(self, msg):
        if not self.verbose: return
        self.app.desk.print(msg)

    def error(self, e, force=False, stop=True):
        if not force and not self.sock: return
        #print(f'** ERROR ** {e}')
        self.app.error(e, 'peer server')
        if stop: self.stop()


class Client(Thread):
    def __init__(self, app, pub_key, host, port, verbose=True):
        super().__init__(name='peer-client')
        self.app = app
        self.verbose = verbose

        self.pub_key = pub_key
        self.host = host
        self.port = port

        self.peer = None
        self.input = Queue(maxsize=1)

        self.ping = None

        self.sender_thread = Thread(
            name='peer-client-sender', target=self.sender)
        self.receiver_thread = Thread(
            name='peer-client-receiver', target=self.receiver)

    def run(self):
        addr = (self.host, self.port)
        self.print(f'connecting to peer at {addr}')

        try:
            sock = socket.create_connection(addr, timeout=HELLO_TIMEOUT)
            sock.settimeout(HELLO_TIMEOUT)
            self.peer = Handler(sock, addr,
                self.app.server.crypto, self.app.server.priv_key, self.pub_key)
            self.peer.hello()
            self.peer.sock.settimeout(GENERAL_TIMEOUT)
            #self.print('[READY]')
            #self.print(f'crypto: {self.peer.crypto}')
            #self.print(f'priv_key: {self.peer.priv_key}')

        except ConnectionRefusedError:
            self.error(f'[CONNECTION REFUSED] {addr}', True)
            self.peer = None

        except socket.timeout:
            self.error(f'[CONNECTION TIMEOUT] {addr}', True)
            self.peer = None

        if not self.peer: return
        self.receiver_thread.start()
        self.sender_thread.start()

        label = self.app.server.label
        self.ping = Ping(label)
        self.input.put_nowait(self.ping)

    def text(self, txt):
        self.input.put_nowait(Text(txt))

    def on_text(self, msg, handler):
        self.print(f'client got text: {msg}')

    def stop(self):
        if not self.peer: return
        #self.print('peer client stopping')

        peer = self.peer
        self.peer = None

        peer.sock.shutdown(socket.SHUT_RDWR)
        peer.sock.close()
        #self.output.put_nowait(None)
        self.input.put_nowait(None)

        #import traceback
        #for line in traceback.format_stack():
        #    self.print(f'TRACE: {line.strip()}')

    def join(self):
        self.receiver_thread.join()
        self.sender_thread.join()
        super().join()

    def sender(self):
        #self.print('sender')
        try:
            while self.peer:
                #self.print('checking input queue')
                try:
                    #while msg := self.input.get(timeout=KEEPALIVE):
                    msg = self.input.get(timeout=KEEPALIVE)
                    if msg:
                        if not self.peer: break
                        self.send(msg)

                except Empty:
                    if self.ping:
                        return self.error('ping sent but no pong received')

                    if self.peer:
                        self.ping = Ping(self.app.server.label)
                        self.send(self.ping)

        finally:
            #self.print('sender out')
            self.stop()

    def send(self, msg):
        if not self.peer: return
        self.print(f'C    {self.peer.addr} <- {msg}')
        self.peer.send(msg)

    def receiver(self):
        try:
            #while msg := self.recv():
            msg = self.recv()
            while msg:
                if isinstance(msg, Pong):
                    if not self.ping:
                        return self.error(f'received pong without ping: {msg}')

                    if msg.nonce != self.ping.nonce:
                        return self.error(f'ping-pong nonce mismatch')

                    self.ping = None

                else:
                    #self.output.put(msg)
                    self.print(f'unhandled message: {msg}')

                msg = self.recv()

            self.error('lost connection')

        except OSError as e:
            self.error(e)

        except Exception as e:
            self.error(e)

        finally:
            #self.print('receiver out')
            self.stop()

    def recv(self):
        if not self.peer: return None
        msg = self.peer.recv(self)
        if msg: self.print(f'C    {self.peer.addr} -> {msg}')
        return msg

    def print(self, msg):
        if not self.verbose: return
        self.app.desk.print(msg)

    def error(self, e, force=False):
        #txt = f'{e}'
        #if not txt: txt = type(e)
        #self.print(f'** PEER CLIENT ERROR ** {txt}')
        if not force and not self.peer: return
        self.app.error(e, 'peer client')
        self.stop()

