import wx
import os
import glob
import uuid
import json
import shutil
import hashlib

from datetime import datetime

from .document import Document


class Library():
    def __init__(self, dir):
        wx.LogDebug(f'Initializing Library at {dir}')
        self.dir = dir
        self.documents = []
        for json_path in glob.glob(f'{dir}/*/*/*/*.json'):
            doc = Document(json_path)
            wx.LogDebug(doc.uuid)
            if doc.md5 in self.md5s:
                # TODO: Alert user to duplicate and ask if we can remove
                wx.LogDebug(f"Skipping {doc.json_path}")
            else:
                self.documents.append(doc)

    @property
    def md5s(self):
        return [doc.md5 for doc in self.documents]

    def import_pdf(self, src):
        wx.LogDebug('Importing document to Library')
        date = datetime.now()
        with open(src, 'rb') as file:
            src_md5 = hashlib.md5(file.read()).hexdigest()
        for doc in self.documents:
            wx.LogDebug(f'Looking at {doc.json_path}')
            if 'import' in doc.json:
                if doc.json['import']['md5'] == src_md5:
                    wx.LogDebug('Not importing duplicate')
                    return False
        ext = os.path.splitext(src)[1]
        dir = os.path.join(self.dir,
                           date.strftime('%Y'),
                           date.strftime('%m'),
                           date.strftime('%d'))
        wx.LogDebug(f"Creating {dir} if it doesn't already exist.")
        os.makedirs(dir, exist_ok=True)
        uid = uuid.uuid4().hex
        while glob.glob(os.path.join(dir, uid)):
            wx.LogDebug("You should buy a lottery ticket.")
            uid = uuid.uuid4()
        wx.LogDebug(f'Document UUID is {uuid}')
        path = os.path.join(dir, uid+ext)
        wx.LogDebug(f'Document path is {path}')
        shutil.copy2(src, path)
        with open(path, 'rb') as file:
            dst_md5 = hashlib.md5(file.read()).hexdigest()
        assert src_md5 == dst_md5
        json_filepath = os.path.join(dir, uid+'.json')
        json_dict = {
            'import': {
                'timestamp': datetime.now(),
                'source': src,
                'md5': dst_md5
            }
        }
        with open(json_filepath, 'w') as file:
            json.dump(json_dict, file, indent=3, default=str)
        self.documents.append(Document(json_filepath))
        return self.documents[-1]
