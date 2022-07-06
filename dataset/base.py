from pandas import DataFrame


class Panda:
    def __init__(self, data):
        self._df = DataFrame(data)

    @property
    def df(self):
        return self._df