import datetime

from dateutil.parser import parse

from .bagofwords import BagOfWords


class Date(BagOfWords):

    @staticmethod
    def today():
        return datetime.date.today()

    def __init__(self, words):
        super().__init__(words)
        self.dt = parse(self.text, fuzzy=True)
        self.range = None
        for word in self.words:
            word.date = self

    def __lt__(self, other):
        return self.dt < other.dt

    def __repr__(self):
        return str(self.dt)

    @property
    def year(self):
        return self.dt.strftime('%Y')

    @property
    def month(self):
        return self.dt.strftime('%m')

    @property
    def day(self):
        return self.dt.strftime('%d')


class DateRange(BagOfWords):
    def __init__(self, start, end):
        super().__init__([start, end])
        self.start = parse(start.text)
        self.end = parse(end.text)
        start.range = self
        end.range = self
