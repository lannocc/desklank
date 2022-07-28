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

        self.elements = [
            'sign on',
            'register',
        ]
        self.el_width = 0
        for el in self.elements:
            self.el_width += len(el)

        self.max_w -= 2
        self.max_h -= 3

        if len(self.elements) * 4 + self.el_width > self.max_w:
            raise RuntimeError('screen not wide enough')

        self.register_module()

    def page(self, panel):
        el_count = len(self.elements)
        w = int((self.max_w - self.el_width - 4 * el_count) / (el_count + 1))
        h = 1

        for idx, el in enumerate(self.elements):
            color = self.frontend.color_gb if idx == self.cur_el \
                else self.frontend.chess_white

            panel.addstr(1, h + w, f'< {el} >' if idx == self.cur_el \
                                else f'[ {el} ]', color)
            h += w + 4 + len(el)

        if self.cur_el == 0:
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
                    panel.addstr(idx+3, 2, label)
                else:
                    panel.addstr(idx+3, 1, self.app.tw(13))

                panel.addstr(idx+3, 14, value, self.frontend.color_rw
                    if idx == self.scroll else self.frontend.chess_white)

        elif self.cur_el == 1:
            self.scroll_elements = [ ]
            panel.addstr(3, 2, self.app.tw(self.max_w - 1, 'Coming soon'))
            for y in range(4, self.max_h + 1):
                panel.addstr(y, 1, self.app.tw(self.max_w))

    def string_decider(self, panel, txt):
        if self.cur_el == 0:
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
        if self.cur_el == 0:
            if self.scroll == 0:
                if self.app.data['connect'] is None:
                    self.app.top.connect(self.port, self.label, self.pwd,
                                         self.alias)

                else:
                    self.app.top.disconnect()

