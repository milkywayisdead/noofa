from collections import deque


class DfStack(deque):
    @property
    def current(self):
        try:
            return self[-1]
        except IndexError:
            pass

    @current.setter
    def current(self, value):
        self.append(value)