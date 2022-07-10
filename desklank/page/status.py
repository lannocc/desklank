import deskapp

import random


classID = random.random()

class Module(deskapp.Module):
    name = "FIXME"

    def __init__(self, app):
        super().__init__(app)
        self.classID = classID
        self.elements = [
            'foo',
            'bar',
        ]

        self.register_module()

    def page(self, panel):
        panel.addstr(1, 1, 'foobar')


if __name__ == "__main__":
    deskapp.App([Module]).start()

