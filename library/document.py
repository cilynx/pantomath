import wx
import os
import json
import glob
import hashlib


class Document():

    def __init__(self, id=None):
        self.id = id

        self.raw = None
        self.json = None
        self.processed = None

        self.raw_path = None
        self.json_path = None
        self.processed_path = None

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

    def load_json(self, json_path):
        self.json_path = json_path
        with open(self.json_path, 'r') as json_file:
            self.json = json.load(json_file)
        parts = list(os.path.split(json_path))
        json_filename = parts.pop()
        self.uuid = json_filename.split('.')[0]
        self.filedir = parts.pop()
        path = self.filedir.split(os.sep)
        self.day = path.pop()
        self.month = path.pop()
        self.year = path.pop()
        self.lib_dir = os.sep.join(path)

    def write_json(self):
        with open(self.json_path, 'w') as file:
            json.dump(self.json, file, indent=3, sort_keys=True)

    def write_files(self):
        # self.write_raw()
        self.write_json()
        # self.write_processed()

    def delete_files(self):
        for file in self.files:
            os.remove(file)

    ###########################################################################
    # Properties
    ###########################################################################

    @property
    def files(self):
        return glob.glob(self.root + '*')

    @property
    def root(self):
        return os.path.join(self.filedir, self.uuid)

    @property
    def ext(self):
        return self.processed_file_path.split('.')[1]

    @property
    def md5(self):
        if 'md5' not in self.json:
            if 'import' in self.json and 'md5' in self.json['import']:
                self.json['md5'] = self.json['import']['md5']
                del self.json['import']['md5']
            else:
                with open(self.processed_file_path, 'rb') as file:
                    self.json['md5'] = hashlib.md5(file.read()).hexdigest()
            self.write_json()
        assert len(self.json['md5']) == 32
        return self.json['md5']

    @property
    def processed_file_path(self):
        if 'files' not in self.json:
            path = os.path.join(self.filedir, self.uuid + '.*')
            wx.LogDebug(path)
            doc_files = glob.glob(path)
            wx.LogDebug(str(doc_files))
            doc_files.remove(self.json_path)
            assert len(doc_files) == 1
            processed = doc_files[0]
            self.json['files'] = {'processed': processed}
            self.write_json()
        return self.json['files']['processed']
