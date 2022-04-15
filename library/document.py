import wx
import os
import json


class Document():

    def __init__(self, json_path):
        with open(json_path, 'r') as json_file:
            self.json = json.load(json_file)
        self.json_path = json_path
        wx.LogDebug(json_path)
        parts = list(os.path.split(json_path))
        json_filename = parts.pop()
        wx.LogDebug(f'json_filename: {json_filename}')
        self.uuid = json_filename.split('.')[0]
        wx.LogDebug(f'uuid: {self.uuid}')
        path = parts.pop().split(os.sep)
        self.day = path.pop()
        wx.LogDebug(f'day: {self.day}')
        self.month = path.pop()
        wx.LogDebug(f'month: {self.month}')
        self.year = path.pop()
        wx.LogDebug(f'year: {self.year}')
        self.lib_dir = os.sep.join(path)
        wx.LogDebug(f'lib_dir: {self.lib_dir}')
