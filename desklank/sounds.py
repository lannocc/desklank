from beepy import beep

from threading import Thread
from queue import Queue


class Beeper(Thread):
    def __init__(self):
        super().__init__(name='sounds')

        self.go = False
        self.queue = Queue()

    def run(self):
        self.go = True

        while self.go:
            sound = self.queue.get()

            if sound:
                beep(sound)

    def stop(self):
        self.go = False
        self.queue.put(None)

    def beep(self, sound):
        self.queue.put(sound)

