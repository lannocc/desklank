from .. import config

import deskapp
from lank.peer import DEFAULT_PORT

import random


CLASS_ID = random.random()

class Module(deskapp.Module):
    name = 'Connect'

    def __init__(self, app):
        super().__init__(app)
        self.classID = CLASS_ID

        self.port = DEFAULT_PORT
        self.alias = config.load_connect_alias() or ''
        self.label = config.load_connect_label() or 'anonymous'
        self.pwd = ''
        self.app.data['connect'] = None

        self.register_module()

    def page(self, panel):
        pwd_masked = '*' * len(self.pwd)
        connect = self.app.data['connect']
        connect = 'Disconnect' if connect else 'Cancel' \
                    if connect == False else 'Connect'
        #w = self.max_w - 2
        w = 22

        self.scroll_elements = [
            (None, self.app.tw(12, f'[{connect}]')),
            ('Local Port:', self.app.tw(w, self.port)),
            ('     Alias:', self.app.tw(w, self.alias)),
            ('     Label:', self.app.tw(w, self.label)),
            ('  Password:', self.app.tw(w, pwd_masked)),
        ]

        for idx, (label, value) in enumerate(self.scroll_elements):
            if label:
                panel.addstr(idx+2, 2, label)

            panel.addstr(idx+2, 14, value, self.frontend.color_rw
                if idx == self.scroll else self.frontend.chess_white)

    def string_decider(self, panel, txt):
        if self.scroll == 1:
            try: self.port = int(txt)
            except ValueError: pass
        elif self.scroll == 2:
            self.alias = txt
            self.app.print(self.alias)
        elif self.scroll == 3:
            self.label = txt
        elif self.scroll == 4:
            self.pwd = txt

    @deskapp.callback(CLASS_ID, deskapp.Keys.ENTER)
    def on_enter(self, *args, **kwargs):
        if self.scroll == 0:
            if self.app.data['connect'] is None:
                self.app.top.connect(self.port, self.label, self.pwd,
                                     self.alias)

            else:
                self.app.top.disconnect()

