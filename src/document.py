import wx
import os
import PIL
import json
import pytesseract

from pytesseract import Output

from .page import Page
from .block import Block
from .paragraph import Paragraph
from .line import Line
from .word import Word
from .date import Date
from .image import Image
from .original import Original


class Document():

    def __init__(self, id=None, pages=None):
        self.id = id

        self._processed = None
        self._json_path = None
        self._thumbnail = None
        self._json = {'imported': Date.today()}
        self._date = None
        self._dates = []
        self._pages = []

        self.original = Original(pages)

    ###########################################################################
    # Factory Methods
    ###########################################################################

    @classmethod
    def from_json(cls, json_path):
        """
        JSON constructor

        Takes in an absolute path to a JSON file
        Returns a ready-to-use Document object
        """
        doc = cls()
        doc.load_json(json_path)
        return doc

    ###########################################################################
    # Object Manipulation
    ###########################################################################

    def merge(self, doc):
        for key in doc.json:
            if key in self.json and doc.json[key] != self.json[key]:
                dialog = wx.MessageDialog(None,
                                          key,
                                          'Which value should we keep?',
                                          wx.YES_NO)
                dialog.SetYesNoLabels(str(self.json[key]), str(doc.json[key]))
                result = dialog.ShowModal()
                if result == wx.ID_YES:
                    pass
                elif result == wx.ID_NO:
                    self.json[key] = doc.json[key]
                else:
                    raise ValueError()  # TODO: Handle this more gracefully
            else:
                self.json[key] = doc.json[key]
        self.write_json()

    ###########################################################################
    # File I/O
    ###########################################################################

    def write_original(self):
        self.original.save(self.original_path)

    def load_json(self, json_path):
        self.json_path = json_path
        with open(self.json_path, 'r') as json_file:
            self.json = json.load(json_file)

    def write_json(self):
        with open(self.json_path, 'w') as file:
            json.dump(self.json, file, indent=3, sort_keys=True, default=str)

    def write_processed(self):
        wx.LogDebug('Document.write_processed(): Getting Sandwich PDF')
        wx.LogDebug(f'self.processed has {self.processed.n_frames} pages')
        self.processed.save(f'{self.id}.tiff',
                            compression='lzma',
                            lossless=True,
                            save_all=True)
        data = pytesseract.image_to_pdf_or_hocr(f'{self.id}.tiff', extension='pdf')
        os.remove(f'{self.id}.tiff')
        wx.LogDebug('Document.write_processed(): Writing Bytes')
        with open(self.processed_path, 'w+b') as file:
            file.write(data)
        wx.LogDebug('Document.write_processed(END)')

    def write_thumb(self):
        wx.LogDebug('write_thumb()')
        self.thumb.save(self.thumb_path)

    def write_files(self, lib_dir):
        self.lib_dir = lib_dir
        os.makedirs(self.folder_path)
        self.write_json()
        self.write_original()
        self.write_processed()
        self.write_thumb()

    def delete_files(self):
        for file in self.files:
            os.remove(file)

    ###########################################################################
    # Collections
    ###########################################################################

    @property
    def blocks(self):
        return [block for page in self.pages for block in page.blocks]

    @property
    def paragraphs(self):
        return [paragraph for block in self.blocks for paragraph in block.paragraphs]

    @property
    def lines(self):
        return [line for paragraph in self.paragraphs for line in paragraph.lines]

    @property
    def words(self):
        return [word for line in self.lines for word in line.words]

    ###########################################################################
    # Properties
    ###########################################################################

    @property
    def thumb(self):
        wx.LogDebug('thumb()')
        if not self._thumbnail:
            self._thumbnail = Image(self.processed).thumbnail()
        return self._thumbnail

    @property
    def processed(self):
        wx.LogDebug('Document.processed()')
        wx.LogDebug(f'Document.processed(): _processed before: {self._processed}')
        if not self._processed:
            pages = [page.deskew().autocrop() for page in self.original.pages]
            pages[0].save(f'{self.id}.tiff',
                          compression='lzma',
                          save_all=True,
                          append_images=pages[1:])
            self._processed = PIL.Image.open(f'{self.id}.tiff')
            os.remove(f'{self.id}.tiff')
        wx.LogDebug(f'Document.processed(): _processed after: {self._processed}')
        wx.LogDebug('Document.processed(END)')
        return self._processed

    @property
    def pages(self):
        wx.LogDebug(f'pages(START): {self._pages}')
        if not self._pages:

            PAGE = 1
            BLOCK = 2
            PARAGRAPH = 3
            LINE = 4
            WORD = 5

            wx.LogDebug('pages(): Loading Tesseract Data')
            data = pytesseract.image_to_data(self.processed,
                                             output_type=Output.DICT)
            wx.LogDebug('pages(): Done with image_to_data()')
            self._json['data'] = data

            page = None
            block = None
            paragraph = None
            line = None
            i = 0
            wx.LogDebug('pages(): Parsing Levels')
            for level in data['level']:
                if level == PAGE:
                    page = Page(self,
                                data['left'][i],
                                data['top'][i],
                                data['width'][i],
                                data['height'][i],
                                data['conf'][i],
                                data['text'][i])
                    self._pages.append(page)
                elif level == BLOCK:
                    block = Block(page,
                                  data['left'][i],
                                  data['top'][i],
                                  data['width'][i],
                                  data['height'][i],
                                  data['conf'][i],
                                  data['text'][i])
                    page.blocks.append(block)
                elif level == PARAGRAPH:
                    paragraph = Paragraph(block,
                                          data['left'][i],
                                          data['top'][i],
                                          data['width'][i],
                                          data['height'][i],
                                          data['conf'][i],
                                          data['text'][i])
                    block.paragraphs.append(paragraph)
                elif level == LINE:
                    line = Line(paragraph,
                                data['left'][i],
                                data['top'][i],
                                data['width'][i],
                                data['height'][i],
                                data['conf'][i],
                                data['text'][i])
                    paragraph.lines.append(line)
                elif level == WORD:
                    if data['text'][i] and not data['text'][i].isspace():
                        word = Word(line,
                                    data['left'][i],
                                    data['top'][i],
                                    data['width'][i],
                                    data['height'][i],
                                    data['conf'][i],
                                    data['text'][i])
                        line.append(word)
                else:
                    raise Exception(f'Unknown level.  Did Tesseract change their TSV spec?: {level}')
                i += 1
        wx.LogDebug('pages(END)')
        return self._pages

    @property
    def dates(self):
        if not self._dates:
            for word in self.words:
                if word.is_date:
                    self._dates.append(Date([word]))
                if word.is_year:
                    self._dates.append(Date([word.prev.prev, word.prev, word]))
        return self._dates

    @property
    def latest_date(self):
        if self.dates:
            return max(self.dates)

    @property
    def date(self):
        if 'date' not in self._json:
            if self.latest_date:
                self._json['date'] = self.latest_date
            else:
                self._json['date'] = Date.today()
        return self._json['date']

    @property
    def year(self):
        if isinstance(self.date.year, str):
            return self.date.year
        else:
            return self.date.strftime('%Y')

    @property
    def month(self):
        if isinstance(self.date.month, str):
            return self.date.month
        else:
            return self.date.strftime('%m')

    @property
    def day(self):
        if isinstance(self.date.day, str):
            return self.date.day
        else:
            return self.date.strftime('%d')

    @property
    def json(self):
        if not self._json:
            with open(self.json_path, 'r') as json_file:
                self._json = json.load(json_file)
        return self._json

    @property
    def folder_path(self):
        wx.LogDebug('Document.folder_path()')
        wx.LogDebug(f'Document.folder_path(): lib_dir: {self.lib_dir}')
        wx.LogDebug(f'Document.folder_path(): year: {self.year}')
        wx.LogDebug(f'Document.folder_path(): month: {self.month}')
        wx.LogDebug(f'Document.folder_path(): day: {self.day}')
        wx.LogDebug(f'Document.folder_path(): id: {self.id}')
        path = os.path.join(self.lib_dir,
                            self.year,
                            self.month,
                            self.day,
                            self.id)
        wx.LogDebug(f'Document.folder_path(): path: {path}')
        return path

    @property
    def json_path(self):
        if not self._json_path:
            self._json_path = os.path.join(self.folder_path, 'props.json')
        return self._json_path

    @json_path.setter
    def json_path(self, value):
        self.folder_path = os.path.dirname(value)

    @property
    def original_path(self):
        return os.path.join(self.folder_path, 'original' + self.original.ext)

    @property
    def thumb_path(self):
        return os.path.join(self.folder_path, 'thumbnail.webp')

    @property
    def processed_path(self):
        return os.path.join(self.folder_path, 'processed.pdf')
