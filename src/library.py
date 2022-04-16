import wx
import os
import glob
import uuid
import json
import shutil
import hashlib
import pytesseract

from datetime import datetime

from .document import Document


class Library():
    def __init__(self, dir):
        wx.LogDebug(f'Initializing Library at {dir}')
        self.dir = dir
        self.documents = []
        for json_path in glob.glob(f'{dir}/*/*/*/*.json'):
            doc = Document.from_json(json_path)
            wx.LogDebug(doc.uuid)
            if doc.md5 in self.md5s:
                dialog = wx.MessageDialog(None,
                                          f'{doc.md5}',
                                          'Merge duplicate entries?',
                                          wx.YES_NO)
                result = dialog.ShowModal()
                if result == wx.ID_YES:
                    self.doc_from_md5(doc.md5).merge(doc)
                    doc.delete()
                wx.LogDebug(f"Skipping {doc.json_path}")
            else:
                self.documents.append(doc)

    def doc_from_md5(self, md5):
        docs = [doc for doc in self.documents if doc.md5 == md5]
        assert len(docs) == 1
        return docs[0]

    @property
    def md5s(self):
        return [doc.md5 for doc in self.documents]

    @property
    def uuids(self):
        return [doc.uuid for doc in self.documents]

    def import_image(self, pil_image):
        wx.LogDebug('Importing PIL Image')
        id = uuid.uuid4()
        while id in self.uuids:
            wx.LogDebug("You should buy a lottery ticket.")
            id = uuid.uuid4()
        # Create Document object
        doc = Document(id)
        # Save the original to Document.raw
        doc.raw = pil_image
        # Process the image to make it OCRable

        # OCR the image and store in Document.json
        doc.json = {
            'text': pytesseract.image_to_data(pil_image,
                                              pytesseract.Output.DICT)
        }
        # Figure out appropriate date (today or from text)
        # and store in Document.json
        # Process the raw image and store in Document.processed
        # Write Document files
        doc.write_files()

    def import_pdf(self, src):
        wx.LogDebug('Importing document to Library')
        date = datetime.now()
        with open(src, 'rb') as file:
            src_md5 = hashlib.md5(file.read()).hexdigest()
        for doc in self.documents:
            wx.LogDebug(f'Looking at {doc.json_path}')
            if doc.md5 == src_md5:
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
                'source': src
            },
            'md5': dst_md5
        }
        with open(json_filepath, 'w') as file:
            json.dump(json_dict, file, indent=3, default=str)
        self.documents.append(Document.from_json(json_filepath))
        return self.documents[-1]
