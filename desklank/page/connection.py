from ..peer import Client as Peer

import deskapp
from deskapp.callback import callbacks
import curses

import random
from datetime import datetime


class Module(deskapp.Module):
    def __init__(self, app, parent, label, alias, address, peer):
        super().__init__(app)
        self.classID = random.random()
        self.parent = parent
        self.label = label
        self.alias = alias
        self.address = address
        self.peer = peer

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

        '''
        self.lines = [f'line {i}' for i in range(100)] #FIXME
        if len(self.lines) > self.max_h:
            self.scroll_elements = [
                None for i in range(len(self.lines) - self.max_h + 1)
            ]
            self.scroll = len(self.scroll_elements) - 1
        else:
            self.scroll_elements = [ None ]
        self.sdiff = len(self.lines) - len(self.scroll_elements)
        '''
        self.lines = [ ]
        self.scroll_elements = [ None ]
        self.sdiff = -1

        self.last_dt = None

        self.register_module()

    def add_history(self, dt, is_self, txt):
        if not (self.last_dt and self.last_dt.date() == dt.date()):
            self.lines.append([dt.strftime('%A, %B %d, %Y'), None, None,
                is_self])

        self.last_dt = dt

        time = f'{int(dt.strftime("%I"))}:{dt.strftime("%M %p")}'
        user = self.label
        if self.alias: user += '/' + self.alias
        user = f'[{user}]'

        rows = [ ]
        pad = len(time) + len(user) + 2
        avail = self.max_w - pad

        if pad > self.max_w - 10:
            raise ValueError('screen width too small: {self.max_w}')

        while len(txt) > avail:
            try:
                space = txt.rindex(' ', 0, avail)
                rows.append(txt[:space])
                txt = txt[space+1:]

            except ValueError:
                rows.append(txt[:avail])
                txt = txt[avail:]

        rows.append(txt)

        self.lines.append([time, user, rows[0], is_self])
        for row in rows[1:]:
            self.lines.append([len(time), len(user), row, is_self])

        if len(self.lines) > self.max_h:
            self.scroll_elements = [
                None for i in range(len(self.lines) - self.max_h + 1)
            ]
            self.scroll = len(self.scroll_elements) - 1

        self.sdiff = len(self.lines) - len(self.scroll_elements)

    def page(self, panel):
        w = int((self.max_w - 2 - self.el_width) / (len(self.elements) + 1))
        h = 1

        for idx, el in enumerate(self.elements):
            color = self.frontend.color_rw if idx == self.cur_el \
                else self.frontend.chess_white

            panel.addstr(1, h + w, el, color)
            h += w + len(el)

        dt_color = self.frontend.chess_white
        self_color = self.frontend.color_gb
        user_color = self.frontend.color_cb

        for v in range(self.max_h):
            y = self.max_h + 1 - v
            idx = self.scroll + self.sdiff - v
            if idx < 0: break

            line = self.lines[idx]
            dt = line[0]
            user = line[1]
            txt = line[2]
            is_self = line[3]

            if isinstance(user, str) and txt:
                panel.addstr(y, 1, dt, dt_color)
                panel.addstr(y, 1 + len(dt), ' ')
                panel.addstr(y, 2 + len(dt), user,
                    self_color if is_self else user_color)
                panel.addstr(y, 2 + len(dt) + len(user), self.app.tw(
                    self.max_w - len(dt) - len(user) - 1, f' {txt}'))

            elif txt:
                panel.addstr(y, 1, self.app.tw(dt + user + 2))
                panel.addstr(y, 3 + dt + user, self.app.tw(
                    self.max_w - dt - user - 2, txt))

            else:
                panel.addstr(y, 1, self.app.tw(self.max_w, dt), dt_color)

    def on_enter(self, *args, **kwargs):
        if self.cur_el == 2:
            # FIXME hack:
            idx = self.app.logic.cur - 1
            while self.app._menu[idx] is not self.parent:
                idx -= 1
            self.app.logic.cur = idx
            del self.app.logic.available_panels[self.name]
            del self.app._menu[self.app._menu.index(self)]

            self.peer.stop()
            self.peer.join()
            self.app.print('all done with connection')

    def string_decider(self, panel, txt):
        if self.cur_el == 0:
            if txt:
                self.add_history(datetime.now(), True, txt)
                self.peer.text(txt)

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

