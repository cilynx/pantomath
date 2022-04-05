#!/usr/bin/env python3

import wx

from objectify import ConfMenu, Scanner


class MainFrame(wx.Frame):
    def __init__(self, *args, **kw):
        super().__init__(*args, **kw)

        self.config = wx.Config("pantomath")

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

        #######################################################################
        # Scanning Menu
        #######################################################################

        scan_menu = wx.Menu()

        duplex_menu = ConfMenu(self, "/Scan")
        duplex_menu.AppendRadioSet(
            {
                'shortHelp': "75dpi",
                'longHelp':  "75dpi",
                'confValue': '75'
            }, {
                'shortHelp': "100dpi",
                'longHelp':  "100dpi",
                'confValue': '100'
            }, {
                'shortHelp': "200dpi",
                'longHelp':  "200dpi",
                'confValue': '200'
            }, {
                'shortHelp': "300dpi",
                'longHelp':  "300dpi",
                'confValue': '300'
            }, {
                'shortHelp': "600dpi",
                'longHelp':  "600dpi",
                'confValue': '600'
            }, {
                'shortHelp': "1200dpi",
                'longHelp':  "1200dpi",
                'confValue': '1200'
            },
            confKey="Resolution"
        )
        scan_menu.AppendSubMenu(duplex_menu, 'Configuration')

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
