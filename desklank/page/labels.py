import deskapp

import random


CLASS_ID = random.random()

class Module(deskapp.Module):
    name = 'Labels'

    def __init__(self, app):
        super().__init__(app)
        self.classID = CLASS_ID
        self.register_module()

    def page(self, panel):
        panel.addstr(1, 1, 'foobar') # FIXME

