import wx

from .document import Document


class Library():
    def __init__(self, dir):
        wx.LogDebug(f'Initializing Library at {dir}')
        self.dir = dir

    def new_document(self, src):
        return Document(self, src)
