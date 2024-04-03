import wx
import re
# import dateutil.parser
from thefuzz import fuzz

from .placeable import Placeable

RED = "\033[91m"
GREEN = "\033[92m"
YELLOW = "\033[93m"
BLUE = "\033[94m"
BOLD = "\033[1m"
END = "\033[0m"

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

        # The DMV is a fan of 00/00/YYYY when they don't know the details
        if re.findall(r'/00/', self.text):
            wx.LogDebug(f"{RED}Found a fake DMV date that isn't a date: {self.text}{END}")
            return False

        # m[m]/d[d]/yy[yy]
        wx.LogDebug(f'{BLUE}Checking if{END} {BOLD}{self.text}{END} {BLUE}is a m[m]/d[d]/yy[yy] date{END}')
        match = re.search(r'^(\d{1,2})[/-](\d{1,2})[/-](\d{2}|\d{4})$', self.text)
        if match:
            wx.LogDebug(f'{BOLD}{self.text}{END} {YELLOW}looks a lot like m[m]/d[d]/yy[yy].  Checking ranges to be sure{END}')
            if 0 < int(match.group(1)) < 13 and 0 < int(match.group(2)) < 32:
                newText = '/'.join(match.groups())
                if newText != self.text:
                    wx.LogDebug(f'{YELLOW}Date has extra garbage.  Converting{END} {self.text} {YELLOW}to{END} {newText}')
                    self.text = newText
                wx.LogDebug(f'{GREEN}Found a m[m]/d[d]/yy[yy] date:{END} {BOLD}{self.text}{END}')
                return True
            else:
                wx.LogDebug(f"{RED}Looks like a date, but isn't a date. Possibly bad OCR:{END} {BOLD}{self.text}{END}")
                return False


        # d[d]-month-yy[yy]
        months = '(?:jan|feb|mar|apr|may|jun|jul|aug|sep|oct|nov|dec)[a-z]*'
        match = re.search(r'(\d{1,2})-([a-zA-Z]+)-(\d{2,4})', self.text)
        if match:
            # wx.LogDebug(f"{self.text} is a match")
            if 0 < int(match.group(1)) < 32:
                if re.search(months, match.group(2), re.IGNORECASE):
                    wx.LogDebug(f"Found a d[d]-month-yy[yy] date: {self.text}")
                    return True

    @property
    def is_year(self):
        if self.type == 'year':
            return True
        elif self.type:
            return False

        months = '(?:jan|feb|mar|apr|may|jun|jul|aug|sep|oct|nov|dec)[a-z]*'

        wx.LogDebug(f'{BLUE}Checking if{END} {BOLD}{self.text}{END} {BLUE}is a 2 or 4-digit numbers that might be a year{END}')
        if match := re.search(r'(^\d{2,4}$)', self.text):
            clean_year = match.group(1)
            wx.LogDebug(f'{YELLOW}Could be a year: {match.group(1)}{END}')
            if pw := self.prev:
                wx.LogDebug(f'{BLUE}Evaluating if pw looks like a day-of-month ({END}{BOLD}{pw.text}{END}{BLUE}){END}')
                match = re.search(r'(\d{1,2}),', pw.text)
                if match and 0 < int(match.group(1)) < 32:
                    wx.LogDebug(f'{YELLOW}Could be a day of month: {match.group(1)}{END}')
                    if ppw := pw.prev:
                        wx.LogDebug(f'{BLUE}Evaluating ppw monthness ({END}{BOLD}{ppw.text}{END}{BLUE}){END}')
                        if match := re.search(months, ppw.text, re.IGNORECASE):
                            clean_month = match.group(0)
                            self.text = clean_year
                            self.type = 'year'
                            ppw.text = clean_month
                            ppw.type = 'month'
                            pw.type = 'day'
                            wx.LogDebug(f'{GREEN}Found a three-token date: {ppw.text} {pw.text} {self.text}{END}')
                            return True
                wx.LogDebug(f'{BLUE}Checking if pw is day-month in a single token{END}')
                if day_month := re.search(fr'(\d{{1,2}})-{months}', pw.text, re.IGNORECASE):
                    self.type = 'year'
                    pw.type = 'day-month'
                    wx.LogDebug(f'{GREEN}Found a two-token date:{END} {BOLD}{pw.text} {self.text}{END}')
                    return True
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

    def fuzz_ratio(self, comp):
        return fuzz.ratio(self.text, comp)

    def looks_like(self, comp, min_ratio=75):
        return self.fuzz_ratio(comp) >= min_ratio
