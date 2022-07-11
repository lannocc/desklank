from .__version__ import __version__
from .page.connect import Module as Connect
from .page.labels import Module as Labels
from .page.peers import Module as Peers
from .node import Client as Node

import deskapp
import lank.name

from threading import Thread
import sys


class Application:
    def __init__(self):
        print(f'desklank v{__version__}')
        self.header = 'Peer-to-Peer Encrypted Messaging: Hit Connect to Begin'

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
            demo_mode=False)
        self.desk.top = self
        self.desk.tw = self.tw

        self.node = None

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
        #print('quit')

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

        self.node = Node(self, port, label, pwd, alias,
            self.on_error, self.on_connect, verbose=False)
        self.node.start()

    def disconnect(self):
        if not self.node: return
        self.desk.print('disconnecting')
        node = self.node
        self.node = None
        node.stop()
        node.join()
        self.desk.print('finished')
        self.desk.data['connect'] = None
        self.desk.set_header(
            self.tw(self.desk.frontend.screen_w - 2, self.header))

    def on_error(self, msg):
        self.desk.print(msg)

    def on_connect(self):
        self.desk.data['connect'] = True
        self.desk.print('connected and ready')

        #self.desk.logic.setup_panel(Labels(self.desk))

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

        #else:
        #    print(f'@@ NOTICE [{title}] @@')
        #    print(f'   >>   {msg}')

        self.desk.set_header(self.tw(self.desk.frontend.screen_w - 2,
            f'[{title}] >> {msg}'))

    def tw(self, w, txt, c=' '):
        if not isinstance(txt, str): txt = f'{txt}'
        size = len(txt)
        if size >= w: return txt
        return txt + c*(w-size)

