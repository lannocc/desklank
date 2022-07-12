from .. import config

import deskapp

import random


CLASS_ID = random.random()

class Module(deskapp.Module):
    name = 'Interests'

    def __init__(self, app):
        super().__init__(app)
        self.classID = CLASS_ID

        self.register_module()

    def page(self, panel):
        labels = self.app.data['labels']
        w = self.max_w - 2

        if self.app.top.node:
            self.scroll_elements = [
                ('[Refresh]', 'Select the labels you are interested in:'
                                if labels else None),
            ]

            if labels:
                self.scroll_elements.extend(
                    [('[*]' if label in self.app.top.interests else '[ ]',
                    label) for label in labels])

        else:
            self.scroll_elements = [ ]
            panel.addstr(2, 2, self.app.tw(w-2, 'Not connected'),
                self.frontend.color_cb)

        for idx, (button, label) in enumerate(self.scroll_elements):
            panel.addstr(idx+2, 11-len(button), button, self.frontend.color_rw
                if idx == self.scroll else self.frontend.chess_white)

            panel.addstr(idx+2, 11,
                self.app.tw(w-11, f' {label}' if label else ''))

    @deskapp.callback(CLASS_ID, deskapp.Keys.ENTER)
    def on_enter(self, *args, **kwargs):
        if not self.app.top.node:
            return

        if self.scroll == 0:
            self.app.top.node.get_labels(self.on_labels)

        else:
            label = self.app.data['labels'][self.scroll-1]
            if label in self.app.top.interests:
                del self.app.top.interests[self.app.top.interests.index(label)]
                notify = False
            else:
                self.app.top.interests.append(label)
                notify = True
            config.save_interests(self.app.top.interests)
            self.app.top.node.interest(label, notify)

    def on_labels(self, labels):
        self.app.data['labels'] = sorted(labels)

