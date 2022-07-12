import deskapp
from deskapp.callback import callbacks

import random


class Module(deskapp.Module):
    def __init__(self, app, msg):
        super().__init__(app)
        self.classID = random.random()
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

        callbacks.append({
            'key': deskapp.Keys.ENTER,
            'docs': '',
            'func': self.on_enter,
            'classID': self.classID,
        })

        self.register_module()

    def page(self, panel):
        panel.addstr(2, 2, 'coming soon')

    def on_enter(self, *args, **kwargs):
        pass

