#!/usr/bin/env python3

import wx
import os

from datetime import datetime

from src import Scanner, Config, Library, VehiclePage
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
        notebook.AddPage(VehiclePage(notebook), 'Vehicles')

        sizer = wx.BoxSizer()
        sizer.Add(notebook, 1, wx.EXPAND)
        panel.SetSizer(sizer)

        self.CreateMenuBar()

    def CreateFileSystemWatcher(self):
        self._fswatcher = wx.FileSystemWatcher()
        self._fswatcher.Bind(wx.EVT_FSWATCHER, self.OnFSEvent)
        self.inbox = os.path.join(self.library.dir, 'Inbox/')
        os.makedirs(self.inbox, exist_ok=True)
        self._fswatcher.Add(self.inbox)

    def OnFSEvent(self, event):
        flags = {
            wx.FSW_EVENT_CREATE: 'wx.FSW_EVENT_CREATE',
            wx.FSW_EVENT_DELETE: 'wx.FSW_EVENT_DELETE',
            wx.FSW_EVENT_RENAME: 'wx.FSW_EVENT_RENAME',
            wx.FSW_EVENT_MODIFY: 'wx.FSW_EVENT_MODIFY',
            wx.FSW_EVENT_ACCESS: 'wx.FSW_EVENT_ACCESS',
            wx.FSW_EVENT_ATTRIB: 'wx.FSW_EVENT_ATTRIB',
            wx.FSW_EVENT_UNMOUNT: 'wx.FSW_EVENT_UNMOUNT',
            wx.FSW_EVENT_WARNING: 'wx.FSW_EVENT_WARNING',
            wx.FSW_EVENT_ERROR: 'wx.FSW_EVENT_ERROR',
            wx.FSW_EVENT_ALL: 'wx.FSW_EVENT_ALL',
        }
        wx.LogDebug(f'ChangeType: {flags[event.ChangeType]}')
        wx.LogDebug(event.Path)
        self._last_fs_event = datetime.now()
        if event.ChangeType == wx.FSW_EVENT_CREATE or event.ChangeType == wx.FSW_EVENT_RENAME:
            self.ImportFromInbox(event.Path)

    def InboxHasSettled(self):
        return (datetime.now()-self._last_fs_event).total_seconds() > 2

    def ImportFromInbox(self, filepath):
        if self.InboxHasSettled():
            if os.path.exists(filepath):
                wx.LogDebug(f'Importing {filepath}')
                if self.library.import_file(filepath):
                    if self.config.Read("/Import/RemoveSource", ''):
                        wx.LogDebug(f'Removing {filepath}')
                        os.remove(filepath)
            else:
                wx.LogDebug(f'{filepath} no longer exists.  It was probably a browser temp file')
        else:
            wx.LogDebug('Waiting for Inbox to settle')
            wx.CallLater(1000, self.ImportFromInbox, filepath)

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
        self.Bind(wx.EVT_MENU, self.OnImportFile, importItem)

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

        scan_menu.AppendSubMenu(self.scanner.deviceMenu, '&Scanner')
        scan_menu.AppendSubMenu(self.scanner.ConfigMenu(), '&Resolution')
        scan_menu.AppendSubMenu(self.scanner.modeMenu, '&Mode')

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
        # wx.LogDebug(self.scanner.device.__dict__)

    def OnImportFile(self, event):
        filepath = self.ChooseFile()
        if filepath:
            self.library.import_file(filepath)

    # def ImportImage(self, image):
    #     self.PushStatusText("Processing image...", 1)
    #
    #     uid = uuid.uuid4().hex
    #
    #     now = datetime.now()
    #     path = os.path.join(self.library.dir, now.strftime('%Y'), now.strftime('%m'), now.strftime('%d'))
    #     wx.LogDebug(f"ImportImage(): Creating {path} if it doesn't already exist.")
    #     os.makedirs(path, exist_ok=True)
    #     raw = os.path.join(path, uid + "-raw.webp")
    #     wx.LogDebug("Saving raw scan to " + raw)
    #     Image(image).save(raw, lossless=True)
    #
    #     image = Image(image).deskew()
    #     wx.LogDebug(f"BBox: {image.bbox()}")
    #     from PIL import ImageDraw, ImageFilter
    #     draw = ImageDraw.Draw(image.pil_image)
    #     draw.rectangle(image.bbox(), outline=(255, 0, 0))
    #     image.show()
    #     wx.LogDebug(f"Size: {image.size}")
    #     image = image.pil_image.crop(image.bbox())
    #     image = image.filter(ImageFilter.MinFilter())
    #     image.show()
    #
    #     while glob.glob(uid + '.*'):
    #         wx.LogDebug("You should buy a lottery ticket.")
    #         uid = uuid.uuid4()
    #
    #     webp = os.path.join(path, uid + ".webp")
    #     wx.LogDebug("Saving processed image to " + webp)
    #     image.save(webp, lossless=True)
    #
    #     thumb = os.path.join(path, uid + "-thumb.webp")
    #     wx.LogDebug("Saving thumbnail to " + thumb)
    #     image.thumbnail((100, 100))
    #     image.save(thumb)
    #
    #     props = os.path.join(path, uid + ".json")
    #     propDict = {
    #         'scan': {
    #             'timestamp': now,
    #             'devname': self.scanner.devname,
    #             'model': self.scanner.model
    #         }
    #     }
    #     with open(props, 'w') as file:
    #         json.dump(propDict, file, indent=3, default=str)
    #
    #     self.PopStatusText(1)

    def ImportPDF(self, filepath):
        wx.LogDebug(f'ImportPDF({filepath})')
        doc = self.library.import_pdf(filepath)
        if doc is False:
            dialog = wx.MessageDialog(self, f'Document is already in your library.  Delete {filepath}?', style=wx.YES_NO)
            if dialog.ShowModal() == wx.ID_YES:
                wx.LogDebug(f'Removing {filepath}')
                os.remove(filepath)
        elif self.config.Read("/Import/RemoveSource", ''):
            wx.LogDebug(f'Imported {doc.json_path}')
            wx.LogDebug(f'Removing {filepath}')
            os.remove(filepath)

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


class Pantomath(wx.App):
    def __init__(self):
        super().__init__()
        self._initialized = False
        self.m_frame = MainFrame(None, title="Pantomath")

    def OnEventLoopEnter(self, loop):
        wx.LogDebug("Entering event loop.")
        if not self._initialized:
            self.m_frame.CreateFileSystemWatcher()
            self._initialized = True


if __name__ == '__main__':
    app = Pantomath()
    app.m_frame.Show()
    app.m_frame.SetIcon(wx.Icon('pantomath.ico', wx.BITMAP_TYPE_ICO))
    app.MainLoop()
