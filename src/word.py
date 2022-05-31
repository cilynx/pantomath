import wx
import re
# import dateutil.parser

from .placeable import Placeable


class Word(Placeable):
    def __init__(self, line, left, top, width, height, confidence, text):
        super().__init__(left, top, width, height)
        self.line = line
        self.confidence = confidence
        self.text = text
        self.type = None
        self.date = None

    ###########################################################################
    # Properties
    ###########################################################################

    @property
    def paragraph(self):
        return self.line.paragraph

    @property
    def block(self):
        return self.paragraph.block

    @property
    def page(self):
        return self.block.page

    @property
    def prev(self):
        index = self.line.words.index(self)
        if index:
            return self.line.words[index-1]

    @property
    def next(self):
        index = self.line.words.index(self)
        if index+1 < len(self.line.words):
            return self.line.words[index+1]

    @property
    def is_date(self):
        if self.type == 'date':
            return True
        elif self.type:
            return False

        # The DMV is a fan of 00/00/2022 when they don't know the details
        if re.findall(r'/00/', self.text):
            return False

        # m[m]/d[d]/yy[yy]
        match = re.search(r'(\d{1,2})[/-](\d{1,2})[/-](\d{2,4})', self.text)
        if match:
            if 0 < int(match.group(1)) < 13 and 0 < int(match.group(2)) < 32:
                newText = '/'.join(match.groups())
                if newText != self.text:
                    wx.LogDebug(f'Date has extra garbage.  Converting {self.text} to {newText}')
                    self.text = newText
                return True
            else:
                wx.LogDebug(f"Date isn't a date. Possibly bad OCR: {self.text}")
                return False

        # This is overly greedy -- every 4-digit number is assumed
        # to be a year with "today" as the month and day
        #
        # try:
        #     dateutil.parser.parse(self.text)
        #     self.type = 'date'
        #     return True
        # except:
        #     return False

    @property
    def is_year(self):
        if self.type == 'year':
            return True
        elif self.type:
            return False

        months = '(?:jan|feb|mar|apr|may|jun|jul|aug|sep|oct|nov|dec)[a-z]*'

        # Jan(uary) 1, 1970
        # 2 or 4-digit year?
        if match := re.search(r'(\d{2,4})', self.text):
            wx.LogDebug(f'Could be a year: {match.group(1)}')
            # 1 or 2-digit day followed by comma?
            if pw := self.prev:
                match = re.search(r'(\d{1,2}),', pw.text)
                if match and 0 < int(match.group(1)) < 32:
                    wx.LogDebug(f'Could be a day-of-month: {match.group(1)}')
                    # Month?
                    if ppw := pw.prev:
                        wx.LogDebug(f'Testing for monthness: {ppw.text}...')
                        if re.search(months, ppw.text, re.IGNORECASE):
                            wx.LogDebug('yup')
                            self.type = 'year'
                            ppw.type = 'month'
                            pw.type = 'day'
                            return True
                        wx.LogDebug('nope')
        return False

    ###########################################################################
    # Public Methods
    ###########################################################################

    def continues(self, contig):
        if self.next_to(contig.last_word):
            wx.LogDebug(f'{self.text} is next_to {contig.last_word.text}')
            return True
        if self.text == 'Please':
            wx.LogDebug(f'|just_below: {self.just_below(contig)}|aligend_with: {self.aligned_with(contig)}|{contig.text}')
        if self.just_below(contig) and self.aligned_with(contig):
            wx.LogDebug(f'{self.text} is just_below and aligned_with {contig.last_word.text}')
            self.text = f'\n{self.text}'
            return True
        return False
