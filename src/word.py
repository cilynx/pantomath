import re

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

        # 03/21/2022
        if re.findall(r'\d{1,2}/\d{1,2}/\d{2,4}', self.text):
            self.type = 'date'
            return True
        else:
            return False

    @property
    def is_year(self):
        if self.type == 'year':
            return True
        elif self.type:
            return False

        months = '(?:jan|feb|mar|apr|may|jun|jul|aug|sep|oct|nov|dec)[a-z]*'

        # 2 or 4-digit year?
        if re.search(r'\d{2,4}', self.text):
            # 1 or 2-digit day followed by comma?
            pw = self.prev
            if pw and re.search(r'\d{1,2}\,', pw.text) and 0 < int(pw.text) < 32:
                # Month?
                ppw = pw.prev
                if ppw and re.search(months, ppw.text, re.IGNORECASE):
                    self.type = 'year'
                    ppw.type = 'month'
                    pw.type = 'day'
                    return True
        return False

    ###########################################################################
    # Public Methods
    ###########################################################################

    def continues(self, contig):
        if self.next_to(contig.last_word):
            print(f'{self.text} is next_to {contig.last_word.text}')
            return True
        if self.text == 'Please':
            print(f'|just_below: {self.just_below(contig)}|aligend_with: {self.aligned_with(contig)}|{contig.text}')
        if self.just_below(contig) and self.aligned_with(contig):
            print(f'{self.text} is just_below and aligned_with {contig.last_word.text}')
            self.text = f'\n{self.text}'
            return True
        return False
