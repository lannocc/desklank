from .. import config

import deskapp
from deskapp.callback import callbacks
import lank.name

import random


#CLASS_ID = random.random()

class Module(deskapp.Module):
    #name = 'Peer'

    def __init__(self, app, label):
        super().__init__(app)
        self.classID = random.random()
        self.label = label
        self.name = f' + {label}'

        self.history = None

        callbacks.append({
            'key': deskapp.Keys.ENTER,
            'docs': '',
            'func': self.on_enter,
            'classID': self.classID,
        })

        self.register_module()

    def page(self, panel):
        w = self.max_w - 2

        if self.app.top.node:
            self.scroll_elements = [
                ('[Refresh]', 'Recent history:'
                                if self.history else None),
            ]

            if self.history:
                for item in self.history.items:
                    dt = item._to_datetime_(
                        item.timestamp).astimezone().strftime(
                            '%a, %d %b %Y @ %I:%M %p')

                    if item.name == lank.name.REGISTER:
                        self.scroll_elements.append((
                            None,
                            f'{dt}: Created new key-pair'))

                    elif item.name == lank.name.PEER:
                        msg = f'{dt}: Signed on'
                        if ':' in item.key[item.key.index(':')+1:]:
                            alias = item.key[item.key.index(':')+1:]
                            alias = alias[alias.index(':')+1:]
                            msg += f' as {alias}'
                        msg += f' at {item.address}'
                        self.scroll_elements.append(('[connect]', msg))

                    else:
                        self.scroll_elements.append((
                            None,
                            f'{dt}: Did something'))

        else:
            self.scroll_elements = [ ]
            panel.addstr(2, 2, self.app.tw(w-2, 'Not connected'),
                self.frontend.color_cb)

        for idx, (button, label) in enumerate(self.scroll_elements):
            if button:
                panel.addstr(idx+2, 11-len(button), button,
                    self.frontend.color_rw
                    if idx == self.scroll else self.frontend.chess_white)
            else:
                panel.addstr(idx+2, 2, self.app.tw(11))

            panel.addstr(idx+2, 11,
                self.app.tw(w-11, f' {label}' if label else ''))

    def on_enter(self, *args, **kwargs):
        if not self.app.top.node:
            return

        if self.scroll == 0:
            self.app.top.node.get_history(self.label, self.on_history)

    def on_history(self, history):
        self.history = history

