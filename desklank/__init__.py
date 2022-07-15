from .__version__ import __version__
from . import config
from .page.connect import Module as Connect
from .page.labels import Module as Labels
from .page.peers import Module as Peers
from .page.peer import Module as Peer
from .peer import Server
from .node import Client as Node

import deskapp
import lank.name

from threading import Thread
import sys


class Application:
    def __init__(self):
        print(f'desklank v{__version__}')
        self.header = 'Peer-to-Peer Encrypted Communication: Connect to Begin'
        self.verbose = '-v' in sys.argv or '--verbose' in sys.argv

        try:
            from .systray import Icon as TrayIcon
            self.tray_icon = TrayIcon(self)
            self.tray_thread = Thread(target=self.tray_icon.run)

        except Exception as e:
            em = str(e)
            if not em: em = type(e)
            print(f'WARNING - Unable to setup system tray icon: {em}')
            self.tray_icon = None
            self.tray_thread = None

        self.desk = deskapp.App(
            modules=[Connect, Labels, Peers],
            title=f'desklank v{__version__}',
            header=self.header,
            v_split=(0.35 if self.verbose else 0.18),
            h_split=0.2,
            demo_mode=False)
        self.desk.top = self
        self.desk.tw = self.tw
        self.desk.data['labels'] = [ ]

        self.server = None
        self.node = None
        self.interests = config.load_interests()
        self.peers = { label: None for label in config.load_peers() }

        self.finished = False
        self.exiting = False

    def run(self):
        try:
            if self.tray_thread:
                self.tray_thread.start()

            self.desk.start()
            self.finished = True

        except KeyboardInterrupt:
            pass

        finally:
            self.quit()
            if self.tray_thread:
                self.tray_thread.join()

    def quit(self):
        if self.exiting: return
        self.exiting = True

        if self.tray_icon:
            self.tray_icon.stop()

        if not self.finished:
            self.desk.close()

        self.disconnect()

    def connect(self, port, label, pwd, alias):
        self.desk.print('connecting')
        self.desk.data['connect'] = False
        self.desk.set_header(
            self.tw(self.desk.frontend.screen_w - 2, ''))

        self.server = Server(self, label, port, verbose=self.verbose)
        self.server.start()
        self.server.ready.wait()

        if self.server.sock:
            self.node = Node(self, port, label, pwd, alias,
                self.error, self.on_connect, verbose=self.verbose)
            self.node.start()

        else:
            self.disconnect()

    def disconnect(self):
        if not self.server: return
        self.desk.print('disconnecting')
        self.desk.data['labels'] = [ ]

        server = self.server
        self.server = None
        server.stop()
        server.join()

        if self.node:
            node = self.node
            self.node = None
            node.stop()
            node.join()

        self.desk.print('finished')
        self.desk.data['connect'] = None
        self.desk.set_header(
            self.tw(self.desk.frontend.screen_w - 2, self.header))

    def error(self, e, context=None):
        ctxt = f'<{context}> ' if context else ''
        etxt = f'{e}'
        if not etxt: etxt = type(e)
        self.desk.print(f'** ERROR {ctxt}** {etxt}')

    def on_connect(self, labels):
        self.desk.data['connect'] = True
        self.desk.data['labels'] = sorted(labels)

        for label in self.desk.data['labels']:
            if label in self.peers:
                if not self.peers[label]:
                    page = Peer(self.desk, label)
                    self.desk.logic.setup_panel(page)
                    self.peers[label] = page

        self.desk.print('connected and ready')

    def notify(self, signed):
        if signed.name == lank.name.REGISTER:
            self._notify_(signed.label, f'{signed.label} has changed keys')

        elif signed.name == lank.name.PEER:
            msg = f'{signed.label} signed on'
            if ':' in signed.key[signed.key.index(':')+1:]:
                alias = signed.key[signed.key.index(':')+1:]
                alias = alias[alias.index(':')+1:]
                msg += f' as {alias}'
            self._notify_(signed.label, msg)

        else:
            self._notify_(signed.label, f'{signed.label} has done something')

    def _notify_(self, title, msg):
        if self.tray_icon:
            self.tray_icon.notify(msg, f'{title} | desklank')

        self.desk.set_header(self.tw(self.desk.frontend.screen_w - 2,
            f'[{title}] >> {msg}'))

    def tw(self, w, txt='', c=' '):
        if not isinstance(txt, str): txt = f'{txt}'
        size = len(txt)
        if size >= w: return txt
        return txt + c*(w-size)

