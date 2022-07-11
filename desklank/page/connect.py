from .. import config

import deskapp
from lank.peer import DEFAULT_PORT

import random


CLASS_ID = random.random()

class Module(deskapp.Module):
    name = "Connect"

    def __init__(self, app):
        super().__init__(app)
        self.classID = CLASS_ID

        self.port = DEFAULT_PORT
        self.alias = config.load_connect_alias() or ''
        self.label = config.load_connect_label() or 'anonymous'
        self.pwd = ''

        self.register_module()

    def page(self, panel):
        panel.addstr(1, 1, 'foobar')

    def page(self, panel):
        pwd_masked = '*' * len(self.pwd)
        w = 42

        self.scroll_elements = [
            self.tw(w, f'Local Port: {self.port}'),
            self.tw(w, f'     Alias: {self.alias}'),
            self.tw(w, f'     Label: {self.label}'),
            self.tw(w, f'  Password: {pwd_masked}'),
            self.tw(w,  '            [Connect]')
        ]

        for idx, option in enumerate(self.scroll_elements):
            color = self.frontend.color_rw \
                if idx == self.scroll else self.frontend.chess_white
            panel.addstr(idx+2, 4, option, color)

    def tw(self, w, txt):
        size = len(txt)
        if size >= w: return txt
        return txt + ' '*(w-size)

    def string_decider(self, panel, txt):
        if self.scroll == 0:
            try: self.port = int(txt)
            except ValueError: pass
        elif self.scroll == 1:
            self.alias = txt
        elif self.scroll == 2:
            self.label = txt
        elif self.scroll == 3:
            self.pwd = txt
        else:
            raise NotImplementedError()

    @deskapp.callback(CLASS_ID, deskapp.Keys.ENTER)
    def on_enter(self, *args, **kwargs):
        if self.scroll == 4:
            self.app.top.connect(self.port, self.label, self.pwd, self.alias)

if __name__ == "__main__":
    deskapp.App([Module]).start()

