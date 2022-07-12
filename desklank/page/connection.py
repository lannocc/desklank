import deskapp
from deskapp.callback import callbacks
import curses

import random


class Module(deskapp.Module):
    def __init__(self, app, parent, msg):
        super().__init__(app)
        self.classID = random.random()
        self.parent = parent
        self.label = msg.label

        self.alias = ''
        if ':' in msg.key[msg.key.index(':')+1:]:
            alias = msg.key[msg.key.index(':')+1:]
            self.alias = alias[alias.index(':')+1:]
        self.address = msg.address

        #name = '    '
        #if self.alias: name += f'{self.alias} '
        #self.name = f'{name}@ {self.address}'
        if self.alias: name = f' @ {self.alias}'
        else: name = f' @ {self.address}'
        self.name = name

        c = 2
        while name in self.app.logic.available_panels:
            name = f'{self.name} ({c})'
            c += 1
        self.name = name

        self.elements = [
            '[chat]',
            '[file]',
            '[close]',
        ]
        self.el_width = 0
        for el in self.elements:
            self.el_width += len(el)

        callbacks.append({
            'key': deskapp.Keys.ENTER,
            'docs': '',
            'func': self.on_enter,
            'classID': self.classID,
        })

        '''
        callbacks.append({
            'key': deskapp.Keys.UP,
            'docs': '',
            'func': self.on_scroll_up,
            'classID': self.classID,
        })

        callbacks.append({
            'key': deskapp.Keys.DOWN,
            'docs': '',
            'func': self.on_scroll_down,
            'classID': self.classID,
        })
        '''

        callbacks.append({
            'key': curses.KEY_HOME,
            'docs': '',
            'func': self.on_scroll_top,
            'classID': self.classID,
        })

        callbacks.append({
            'key': curses.KEY_END,
            'docs': '',
            'func': self.on_scroll_bottom,
            'classID': self.classID,
        })

        self.max_w -= 2
        self.max_h -= 3

        self.lines = [f'line {i}' for i in range(100)] #FIXME
        if len(self.lines) > self.max_h:
            self.scroll_elements = [
                None for i in range(len(self.lines) - self.max_h + 1)
            ]
            self.scroll = len(self.scroll_elements) - 1
        else:
            self.scroll_elements = [ None ]
        self.sdiff = len(self.lines) - len(self.scroll_elements)

        self.register_module()

    def page(self, panel):
        w = int((self.max_w - 2 - self.el_width) / (len(self.elements) + 1))
        h = 1

        for idx, el in enumerate(self.elements):
            color = self.frontend.color_rw if idx == self.cur_el \
                else self.frontend.chess_white

            panel.addstr(1, h + w, el, color)
            h += w + len(el)

        for v in range(self.max_h):
            y = self.max_h + 1 - v
            idx = self.scroll + self.sdiff - v
            if idx < 0: break
            panel.addstr(y, 1, self.app.tw(self.max_w, self.lines[idx]))

    def on_enter(self, *args, **kwargs):
        if self.cur_el == 2:
            # FIXME hack:
            idx = self.app.logic.cur - 1
            while self.app._menu[idx] is not self.parent:
                idx -= 1
            self.app.logic.cur = idx
            del self.app.logic.available_panels[self.name]
            del self.app._menu[self]

    '''
    #def on_scroll_up(self, *args, **kwargs):
    def on_up(self, *args, **kwargs):
        self.app.print('up')

    #def on_scroll_down(self, *args, **kwargs):
    def on_down(self, *args, **kwargs):
        self.app.print('down')
    '''

    def on_scroll_top(self, *args, **kwargs):
        self.scroll = 0

    def on_scroll_bottom(self, *args, **kwargs):
        self.scroll = len(self.scroll_elements) - 1

