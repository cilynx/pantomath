#!/usr/bin/env python3

import wx


class MainFrame(wx.Frame):
    def __init__(self, *args, **kw):
        super().__init__(*args, **kw)

        panel = wx.Panel(self)

        text = wx.StaticText(panel, label="Pantomath")

        sizer = wx.BoxSizer(wx.VERTICAL)
        sizer.Add(text, wx.SizerFlags().Border(wx.TOP | wx.LEFT, 25))
        panel.SetSizer(sizer)

        self.CreateMenuBar()
        self.CreateStatusBar()
        self.SetStatusText("Welcome to wxPython")

    def CreateMenuBar(self):
        fileMenu = wx.Menu()
        exitItem = fileMenu.Append(wx.ID_EXIT)
        self.Bind(wx.EVT_MENU, self.Exit, exitItem)

        scan_menu = wx.Menu()
        scan_hardware_duplex = scan_menu.AppendRadioItem(wx.ID_ANY, "Hardware &Duplex", "Scan front and back of all pages in ADF using hardware duplexer")
        scan_manual_duplex = scan_menu.AppendRadioItem(wx.ID_ANY, "&Manual Duplex", "Scan front of all pages, flip the stack manually, then scan the backs")
        scan_fronts = scan_menu.AppendRadioItem(wx.ID_ANY, "Only &Fronts", "Scan backs of all pages using hardware duplexer")
        scan_backs = scan_menu.AppendRadioItem(wx.ID_ANY, "Only &Backs", "Scan fronts of all pages")
        fileMenu.AppendSeparator()
        scan_all_from_adf = scan_menu.Append(wx.ID_ANY, "Scan All from &ADF", "Scan all pages from ADF")
        self.Bind(wx.EVT_MENU, self.ScanAllFromADF, scan_all_from_adf)
        scan_one_from_flatbed = scan_menu.Append(wx.ID_ANY, "Scan &One Page from Flatbed", "Scan a single page from the flatbed")
        scan_multiple_from_flatbed = scan_menu.Append(wx.ID_ANY, "Scan Multiple &Pages from Flatbed", "Scan multiple pages from the flatbed glass, one at a time with a confirmation dialog in between each")

        helpMenu = wx.Menu()
        aboutItem = helpMenu.Append(wx.ID_ABOUT)
        self.Bind(wx.EVT_MENU, self.About, aboutItem)

        menuBar = wx.MenuBar()
        menuBar.Append(fileMenu, "&File")
        menuBar.Append(scan_menu, "&Scan")
        menuBar.Append(helpMenu, "&Help")

        self.SetMenuBar(menuBar)

    def ScanAllFromADF(self, event):
        wx.MessageBox("Scan all from ADF is not yet implemented")

    def Exit(self, event):
        self.Close(True)

    def About(self, event):
        wx.MessageBox("Pantomath",
                      "Pantomath knows lots of things.",
                      wx.OK | wx.ICON_INFORMATION)


if __name__ == '__main__':
    app = wx.App()
    frame = MainFrame(None, title="Pantomath")
    frame.Show()
    app.MainLoop()
