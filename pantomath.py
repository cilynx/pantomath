#!/usr/bin/env python3

import wx

from confmenu import ConfMenu


class MainFrame(wx.Frame):
    def __init__(self, *args, **kw):
        super().__init__(*args, **kw)

        self.config = wx.Config("Pantomath")
        print(self.config.Read("/Scan/Duplex"))

        panel = wx.Panel(self)

        text = wx.StaticText(panel, label="Pantomath")

        sizer = wx.BoxSizer(wx.VERTICAL)
        sizer.Add(text, wx.SizerFlags().Border(wx.TOP | wx.LEFT, 25))
        panel.SetSizer(sizer)

        self.CreateMenuBar()
        self.CreateStatusBar()
        self.SetStatusText("Welcome to wxPython")

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

        scan_all_from_adf = scan_menu.Append(wx.ID_ANY, "Scan All from &ADF\tALT-A", "Scan all pages from ADF")
        self.Bind(wx.EVT_MENU, self.ScanAllFromADF, scan_all_from_adf)
        scan_one_from_flatbed = scan_menu.Append(wx.ID_ANY, "Scan &One Page from Flatbed\tALT-O", "Scan a single page from the flatbed")
        self.Bind(wx.EVT_MENU, self.ScanOneFromFlatbed, scan_one_from_flatbed)
        scan_multiple_from_flatbed = scan_menu.Append(wx.ID_ANY, "Scan Multiple &Pages from Flatbed\tALT-P", "Scan multiple pages from the flatbed glass, one at a time with a confirmation dialog in between each")
        self.Bind(wx.EVT_MENU, self.ScanMultipleFromFlatbed, scan_multiple_from_flatbed)

        #######################################################################
        # Help Menu
        #######################################################################

        helpMenu = wx.Menu()
        aboutItem = helpMenu.Append(wx.ID_ABOUT)
        self.Bind(wx.EVT_MENU, self.About, aboutItem)

        #######################################################################
        # The Menu Bar Itself
        #######################################################################

        menuBar = wx.MenuBar()
        menuBar.Append(fileMenu, "&File")
        menuBar.Append(scan_menu, "&Scan")
        menuBar.Append(helpMenu, "&Help")
        self.SetMenuBar(menuBar)

    def ScanAllFromADF(self, event):
        wx.MessageBox("Scan all from ADF is not yet implemented")

    def ScanOneFromFlatbed(self, event):
        wx.MessageBox("Scan one from Flatbed is not yet implemented")

    def ScanMultipleFromFlatbed(self, event):
        wx.MessageBox("Scan multiple from Flatbed is not yet implemented")

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
