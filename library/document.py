import wx
import os
import uuid
import glob
import json
import shutil
import hashlib

from datetime import datetime


class Document():

    def __init__(self, library, src):
        wx.LogDebug('Initializing new Document')
        self.library = library
        self.date = datetime.now()
        self.ext = os.path.splitext(src)[1]
        self.src = src
        wx.LogDebug(f'Document({src})')
        self.dir = os.path.join(self.library.dir,
                                self.date.strftime('%Y'),
                                self.date.strftime('%m'),
                                self.date.strftime('%d'))
        wx.LogDebug(f"Creating {self.dir} if it doesn't already exist.")
        os.makedirs(self.dir, exist_ok=True)
        self.uuid = uuid.uuid4().hex
        while glob.glob(os.path.join(self.dir, self.uuid)):
            wx.LogDebug("You should buy a lottery ticket.")
            self.uuid = uuid.uuid4()
        wx.LogDebug(f'Document UUID is {self.uuid}')
        self.path = os.path.join(self.dir, self.uuid + self.ext)
        wx.LogDebug(f'Document path is {self.path}')
        with open(src, 'rb') as file:
            self.src_md5 = hashlib.md5(file.read()).hexdigest()
        shutil.copy2(src, self.path)
        with open(self.path, 'rb') as file:
            self.md5 = hashlib.md5(file.read()).hexdigest()
        assert self.src_md5 == self.md5
        props = os.path.join(self.dir, self.uuid + '.json')
        propDict = {
            'import': {
                'timestamp': datetime.now(),
                'source': src,
                'md5': self.md5
            }
        }
        with open(props, 'w') as file:
            json.dump(propDict, file, indent=3, default=str)
