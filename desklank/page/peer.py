from .. import config

import deskapp

import random


#CLASS_ID = random.random()

class Module(deskapp.Module):
    #name = 'Peer'

    def __init__(self, app, label):
        super().__init__(app)
        self.classID = random.random()
        self.label = label
        self.name = f' + {label}'

        self.register_module()

    def page(self, panel):
        panel.addstr(2, 2, f'just a test: {self.label}')

