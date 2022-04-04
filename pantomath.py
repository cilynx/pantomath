#!/usr/bin/env python3

import wx
import threading

from objectify import ConfMenu, Scanner


class MainFrame(wx.Frame):
    def __init__(self, *args, **kw):
        super().__init__(*args, **kw)

        self.CreateStatusBar(2)
        self.SetStatusText("Pantomath v0.1")
        self.SetStatusText("Not connected to scanner", 1)

        self.Dispatch(self.InitScanner, "Connecting to scanner...")

        self.config = wx.Config("pantomath")

        panel = wx.Panel(self)

        text = wx.StaticText(panel, label="Pantomath")

        sizer = wx.BoxSizer(wx.VERTICAL)
        sizer.Add(text, wx.SizerFlags().Border(wx.TOP | wx.LEFT, 25))
        panel.SetSizer(sizer)

        self.CreateMenuBar()

    def Dispatch(self, func, status_text='', daemon=True):
        self.PushStatusText(status_text, 1)
        threading.Thread(target=func, daemon=daemon).start()

    def InitScanner(self):
        self.scanner = Scanner()
        self.SetStatusText(self.scanner.model, 1)
        self.scan_all_from_adf.Enable(True)
        self.scan_one_from_flatbed.Enable(True)
        self.scan_multiple_from_flatbed.Enable(True)
        # print(self.scanner.device.__dict__)

    def CreateMenuBar(self):

        #######################################################################
        # File Menu
        #######################################################################

        fileMenu = wx.Menu()
        exitItem = fileMenu.Append(wx.ID_EXIT)
        self.Bind(wx.EVT_MENU, self.Exit, exitItem)

        #######################################################################
        # Scanning Menu
        #######################################################################

        scan_menu = wx.Menu()

        duplex_menu = ConfMenu(self, "/Scan")
        duplex_menu.AppendRadioSet(
            {
                'shortHelp': "Hardware &Duplex",
                'longHelp':  "Scan front and back of all pages in ADF using hardware duplexer",
                'confValue': "Hardware"
            }, {
                'shortHelp': "&Manual Duplex",
                'longHelp': " Scan front of all pages, flip the stack manually, then scan the backs",
                'confValue': "Manual"
            }, {
                'shortHelp': "Only &Fronts",
                'longHelp':  "Scan front of all pages",
                'confValue': "Fronts"
            }, {
                'shortHelp': "Only &Backs",
                'longHelp':  "Scan back of all pages using hardware duplexer",
                'confValue': "Backs"
            },
            confKey="Duplex"
        )
        scan_menu.AppendSubMenu(duplex_menu, 'Duplex')

        scan_menu.AppendSeparator()

        self.scan_all_from_adf = scan_menu.Append(wx.ID_ANY, "Scan All from &ADF\tALT-A", "Scan all pages from ADF")
        self.scan_all_from_adf.Enable(False)
        self.Bind(wx.EVT_MENU, self.ScanAllFromADF, self.scan_all_from_adf)
        self.scan_one_from_flatbed = scan_menu.Append(wx.ID_ANY, "Scan &One Page from Flatbed\tALT-O", "Scan a single page from the flatbed")
        self.scan_one_from_flatbed.Enable(False)
        self.Bind(wx.EVT_MENU, self.ScanOneFromFlatbed, self.scan_one_from_flatbed)
        self.scan_multiple_from_flatbed = scan_menu.Append(wx.ID_ANY, "Scan Multiple &Pages from Flatbed\tALT-P", "Scan multiple pages from the flatbed glass, one at a time with a confirmation dialog in between each")
        self.scan_multiple_from_flatbed.Enable(False)
        self.Bind(wx.EVT_MENU, self.ScanMultipleFromFlatbed, self.scan_multiple_from_flatbed)

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

    def ScanAllFromADF(self, event):
        wx.MessageBox("Scan all from ADF is not yet implemented")

    def ScanOneFromFlatbed(self, event):
        self.PushStatusText("Scanning one page from flatbed", 1)
        threading.Thread(target=self.DoScanOneFromFlatbed).start()

    def DoScanOneFromFlatbed(self):
        self.scanner.get_pil_image().show()
        self.PopStatusText(1)

    def ScanMultipleFromFlatbed(self, event):
        self.PushStatusText("Scanning multiple pages from flatbed", 1)
        threading.Thread(target=self.DoScanMultipleFromFlatbed).start()

    def DoScanMultipleFromFlatbed(self):
        i = 1
        while True:
            self.scanner.get_pil_image().show()
            dialog = wx.MessageDialog(self, "", f"Scanned Page {i}", wx.YES_NO)
            dialog.SetYesNoLabels("Scan Another Page", "All Done")
            result = dialog.ShowModal()
            if result != wx.ID_YES:
                break
            i += 1
        self.PopStatusText(1)

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
