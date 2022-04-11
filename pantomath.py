#!/usr/bin/env python3

import wx
import os
import filetype

from objectify import Scanner, Image, Config
from datetime import datetime


class MainFrame(wx.Frame):
    def __init__(self, *args, **kw):
        super().__init__(*args, **kw)

        self.config = Config("pantomath")

        self._libraryPath = self.config.Read("/Library/Path", '')

        self.libraryPath()

        self.CreateStatusBar(2)
        self.SetStatusText("Pantomath v0.1")
        self.SetStatusText("Not connected to scanner", 1)

        self.scanner = Scanner(self)
        # self.Dispatch(self.InitScanner, "Connecting to scanner...")

        panel = wx.Panel(self)

        text = wx.StaticText(panel, label="Pantomath")

        sizer = wx.BoxSizer(wx.VERTICAL)
        sizer.Add(text, wx.SizerFlags().Border(wx.TOP | wx.LEFT, 25))
        panel.SetSizer(sizer)

        self.CreateMenuBar()

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
        libraryLocation = settingsMenu.Append(wx.ID_ANY, "&Library Location\tALT-L")
        self.Bind(wx.EVT_MENU, self.ChooseLibraryLocation, libraryLocation)
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

        now = datetime.now()
        path = os.path.join(self.libraryPath(), now.strftime('%Y'), now.strftime('%m'), now.strftime('%d'))
        wx.LogDebug(f"ImportImage(): Creating {path} if it doesn't already exist.")
        os.makedirs(path, exist_ok=True)
        raw = os.path.join(path, now.strftime('%H%M%S') + "-raw.webp")
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

        webp = os.path.join(path, now.strftime('%H%M%S') + ".webp")
        wx.LogDebug("Saving processed image to " + webp)
        image.save(webp, lossless=True)

        thumb = os.path.join(path, now.strftime('%H%M%S') + "-thumb.webp")
        wx.LogDebug("Saving thumbnail to " + thumb)
        image.thumbnail((100, 100))
        image.save(thumb)

        self.PopStatusText(1)

    def ImportFile(self, event):
        file = self.OpenFile()
        if file:
            kind = filetype.guess(file.name)
            if not kind:
                wx.MessageBox("Unknown filetype.  Maybe plaintext?")
            elif kind.mime.endswith('/pdf'):
                wx.MessageBox("ImportPDF()")
            elif kind.mime.startswith('image/'):
                self.ImportImage(file.name)
            else:
                wx.MessageBox(f'{kind.mime} import not supported')

    def OpenFile(self):
        with wx.FileDialog(self,
                           "Import file",
                           style=wx.FD_OPEN | wx.FD_FILE_MUST_EXIST
                           ) as fileDialog:

            if fileDialog.ShowModal() == wx.ID_CANCEL:
                return

            filePath = fileDialog.GetPath()
            try:
                with open(filePath, 'r') as file:
                    return file
            except IOError:
                wx.LogError(f'Cannot open file: {filePath}')

    def ChooseLibraryLocation(self, event=None):
        with wx.DirDialog(self,                         # parent
                          "Select Library Directory",   # message
                          "",                           # defaultPath
                          wx.DD_DEFAULT_STYLE           # style
                          ) as dirDialog:

            if dirDialog.ShowModal() == wx.ID_CANCEL:
                return

            self._libraryPath = dirDialog.GetPath()
            self.config.Write("/Library/Path", self._libraryPath)

    def libraryPath(self):
        if self._libraryPath == '':
            wx.MessageBox("Please choose where to store your library.\n\nThis is where all of your imported files will live.")
            self.ChooseLibraryLocation()
        return self._libraryPath

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
