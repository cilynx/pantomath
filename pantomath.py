#!/usr/bin/env python3

import wx
import os
import json
import uuid
import glob
import filetype

from datetime import datetime

from objectify import Scanner, Image, Config
from library import Library

from pages import Documents, Organizations


class MainFrame(wx.Frame):
    def __init__(self, *args, **kw):
        super().__init__(*args, **kw)

        self.config = Config("pantomath")
        self.library = Library(self.GetLibraryDir())

        self.CreateStatusBar(2)
        self.SetStatusText("Pantomath v0.1")
        self.SetStatusText("Not connected to scanner", 1)

        self.scanner = Scanner(self)

        panel = wx.Panel(self)
        notebook = wx.Notebook(panel)
        docsPage = Documents(notebook)
        orgsPage = Organizations(notebook)

        notebook.AddPage(docsPage, 'Documents')
        notebook.AddPage(orgsPage, 'Organizations')

        sizer = wx.BoxSizer()
        sizer.Add(notebook, 1, wx.EXPAND)
        panel.SetSizer(sizer)

        self.CreateMenuBar()

    def GetLibraryDir(self):
        dir = self.config.Read("/Library/Path", '')
        if dir == '':
            wx.MessageBox("Please choose where to store your library.\n\nThis is where all of your imported files will live.")
            dir = self.ChooseLibraryDir()
        return dir

    def ChooseLibraryDir(self, event=None):
        with wx.DirDialog(self,                         # parent
                          "Select Library Directory",   # message
                          "",                           # defaultPath
                          wx.DD_DEFAULT_STYLE           # style
                          ) as dirDialog:
            if dirDialog.ShowModal() == wx.ID_CANCEL:
                return
        dir = dirDialog.GetPath()
        self.config.Write("/Library/Path", dir)
        return dir

    def OnRIO(self, event):
        self.config.WriteBool("/Import/RemoveSource", self.rio.IsChecked())

    def CreateMenuBar(self):

        #######################################################################
        # File Menu
        #######################################################################

        fileMenu = wx.Menu()
        exitItem = fileMenu.Append(wx.ID_EXIT)
        self.Bind(wx.EVT_MENU, self.Exit, exitItem)
        importItem = fileMenu.Append(wx.ID_ANY, "&Import File\tALT-I")
        self.Bind(wx.EVT_MENU, self.ImportFile, importItem)

        settingsMenu = wx.Menu()
        libraryLocation = settingsMenu.Append(wx.ID_ANY, "Update &Library Location\tALT-L")
        self.Bind(wx.EVT_MENU, self.ChooseLibraryDir, libraryLocation)
        self.rio = settingsMenu.Append(wx.ID_ANY, "&Remove Imported Originals\tALT-R", kind=wx.ITEM_CHECK)
        self.Bind(wx.EVT_MENU, self.OnRIO, self.rio)
        riostate = self.config.ReadBool("/Import/RemoveSource", False)
        self.rio.Check(riostate)
        fileMenu.AppendSubMenu(settingsMenu, '&Settings')

        #######################################################################
        # Scanning Menu
        #######################################################################

        scan_menu = wx.Menu()

        scan_menu.AppendSubMenu(self.scanner.ConfigMenu(), '&Resolution')

        scan_menu.AppendSeparator()

        self.scan_adf = scan_menu.Append(wx.ID_ANY, "Fronts from &ADF\tALT-A", "Fronts from ADF")
        self.Bind(wx.EVT_MENU, self.scanner.scan_adf, self.scan_adf)
        self.scan_hardware_duplex = scan_menu.Append(wx.ID_ANY, "Hardware &Duplex from ADF\tALT-D", "Hardware duplex all pages from ADF")
        self.Bind(wx.EVT_MENU, self.scanner.scan_hardware_duplex, self.scan_hardware_duplex)
        self.scan_manual_duplex = scan_menu.Append(wx.ID_ANY, "&Manual Duplex from ADF\tALT-M", "Manual duplex all pages from ADF")
        self.Bind(wx.EVT_MENU, self.scanner.scan_manual_duplex, self.scan_manual_duplex)
        self.scan_one_from_flatbed = scan_menu.Append(wx.ID_ANY, "&One Page from Flatbed\tALT-O", "Single page from the flatbed")
        self.Bind(wx.EVT_MENU, self.scanner.scan_one_from_flatbed, self.scan_one_from_flatbed)
        self.scan_multiple_from_flatbed = scan_menu.Append(wx.ID_ANY, "Multiple &Pages from Flatbed\tALT-P", "Multiple pages from the flatbed glass, one at a time with a confirmation dialog in between each")
        self.Bind(wx.EVT_MENU, self.scanner.scan_multiple_from_flatbed, self.scan_multiple_from_flatbed)

        self.EnableScanUI(False)

        #######################################################################
        # Help Menu
        #######################################################################

        helpMenu = wx.Menu()
        aboutItem = helpMenu.Append(wx.ID_ABOUT)
        self.Bind(wx.EVT_MENU, self.About, aboutItem)

        #######################################################################
        # The Menu Bar Itself
        #######################################################################

        menu_bar = wx.MenuBar()
        menu_bar.Append(fileMenu, "&File")
        menu_bar.Append(scan_menu, "&Scan")
        menu_bar.Append(helpMenu, "&Help")
        self.SetMenuBar(menu_bar)

    def EnableScanUI(self, state=True):
        self.scan_adf.Enable(state)
        self.scan_manual_duplex.Enable(state)
        self.scan_hardware_duplex.Enable(state)
        self.scan_one_from_flatbed.Enable(state)
        self.scan_multiple_from_flatbed.Enable(state)
        # print(self.scanner.device.__dict__)

    def ImportImage(self, image):
        self.PushStatusText("Processing image...", 1)

        uid = uuid.uuid4().hex

        now = datetime.now()
        path = os.path.join(self.libraryPath(), now.strftime('%Y'), now.strftime('%m'), now.strftime('%d'))
        wx.LogDebug(f"ImportImage(): Creating {path} if it doesn't already exist.")
        os.makedirs(path, exist_ok=True)
        raw = os.path.join(path, uid + "-raw.webp")
        wx.LogDebug("Saving raw scan to " + raw)
        Image(image).save(raw, lossless=True)

        image = Image(image).deskew()
        print(f"BBox: {image.bbox()}")
        from PIL import ImageDraw, ImageFilter
        draw = ImageDraw.Draw(image.pil_image)
        draw.rectangle(image.bbox(), outline=(255, 0, 0))
        image.show()
        print(f"Size: {image.size}")
        image = image.pil_image.crop(image.bbox())
        image = image.filter(ImageFilter.MinFilter())
        image.show()

        while glob.glob(uid + '.*'):
            wx.LogDebug("You should buy a lottery ticket.")
            uid = uuid.uuid4()

        webp = os.path.join(path, uid + ".webp")
        wx.LogDebug("Saving processed image to " + webp)
        image.save(webp, lossless=True)

        thumb = os.path.join(path, uid + "-thumb.webp")
        wx.LogDebug("Saving thumbnail to " + thumb)
        image.thumbnail((100, 100))
        image.save(thumb)

        props = os.path.join(path, uid + ".json")
        propDict = {
            'scan': {
                'timestamp': now,
                'devname': self.scanner.devname,
                'model': self.scanner.model
            }
        }
        with open(props, 'w') as file:
            json.dump(propDict, file, indent=3, default=str)

        self.PopStatusText(1)

    def ImportPDF(self, filepath):
        wx.LogDebug(f'ImportPDF({filepath})')
        doc = self.library.new_document(filepath)
        if self.config.Read("/Import/RemoveSource", ''):
            if doc.md5 == doc.src_md5:
                wx.LogDebug(f'Removing {filepath}')
                os.remove(filepath)
        wx.LogDebug(f'Imported {doc.path}')

    def ImportFile(self, event):
        filepath = self.ChooseFile()
        kind = filetype.guess(filepath)
        if not kind:
            wx.MessageBox("Unknown filetype.  Maybe plaintext?")
        elif kind.mime.endswith('/pdf'):
            self.ImportPDF(filepath)
        elif kind.mime.startswith('image/'):
            self.ImportImage(filepath)
        else:
            wx.MessageBox(f'{kind.mime} import not supported')

    def ChooseFile(self):
        with wx.FileDialog(self,
                           "Import file",
                           style=wx.FD_OPEN | wx.FD_FILE_MUST_EXIST
                           ) as fileDialog:
            if fileDialog.ShowModal() == wx.ID_CANCEL:
                return
            return fileDialog.GetPath()

    def Exit(self, event):
        self.Close(True)

    def About(self, event):
        wx.MessageBox("Pantomath knows lots of things.",
                      "Pantomath",
                      wx.OK | wx.ICON_INFORMATION)


if __name__ == '__main__':
    app = wx.App()
    frame = MainFrame(None, title="Pantomath")
    frame.Show()
    app.MainLoop()
