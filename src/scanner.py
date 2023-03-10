import wx
import sane
import threading

from .confmenu import ConfMenu


class Scanner():
    """
    A simple Scanner object
    """

    def __init__(self, frame):
        self.frame = frame
        self.options = {}
        self.modeMenu = ConfMenu(self.frame, "/Scan")
        self.PushStatusText("Initializing scanner...")
        threading.Thread(target=self._init_scanner, daemon=True).start()

    def __del__(self):
        self.device.close()

    def __getattr__(self, name):
        return self.device.__getattribute__(name)

    ###########################################################################
    # Status Management
    ###########################################################################

    def PushStatusText(self, text):
        return self.frame.PushStatusText(text, 1)

    def PopStatusText(self):
        return self.frame.PopStatusText(1)

    ###########################################################################
    # Config Menu
    ###########################################################################

    def ConfigMenu(self):
        menu = ConfMenu(self.frame, "/Scan")
        menu.AppendRadioSet(
            {
                'shortHelp': "75dpi",
                'longHelp':  "75dpi",
                'confValue': '75'
            }, {
                'shortHelp': "100dpi\tALT-1",
                'longHelp':  "100dpi",
                'confValue': '100'
            }, {
                'shortHelp': "200dpi\tALT-2",
                'longHelp':  "200dpi",
                'confValue': '200'
            }, {
                'shortHelp': "300dpi\tALT-3",
                'longHelp':  "300dpi",
                'confValue': '300'
            }, {
                'shortHelp': "600dpi\tALT-6",
                'longHelp':  "600dpi",
                'confValue': '600'
            }, {
                'shortHelp': "1200dpi",
                'longHelp':  "1200dpi",
                'confValue': '1200'
            },
            confKey="Resolution"
        )
        return menu

    ###########################################################################
    # Blocking Functions: All _functions would block the UI if
    #                     not dispatched in separate threads
    ###########################################################################

    def _init_scanner(self):
        wx.LogDebug('Initializing scanner')
        self.sane_version = sane.init()
        while True:
            try:
                devices = sane.get_devices()
                if devices:
                    wx.LogDebug(repr(devices))
                    self.devname, self.vendor, self.model, self.type = devices[0]
                    self.device = sane.open(self.devname)
                    wx.CallAfter(self.PushStatusText, self.model + " Ready")
                    wx.LogDebug('Enabling Scan UI')
                    for option in self.device.get_options():
                        self.options[option[1]] = option[8]
                    modeOptions = [{'shortHelp': mode, 'longHelp': mode, 'confValue': mode} for mode in self.options['mode']]
                    self.modeMenu.AppendRadioSet(*modeOptions, confKey="Mode")
                    self.frame.EnableScanUI()
                else:
                    wx.LogDebug('No scanner found')
                    wx.CallAfter(self.PushStatusText, 'No scanner found')
                break
            except sane._sane.error as e:
                wx.LogDebug(repr(e))

    def scan_hardware_duplex(self, event=None):
        self.PushStatusText("Scanning pages from ADF hardware duplexer.")
        self.frame.config.Write('/Scan/Source', 'ADF Duplex')
        self.pages = []
        thread = threading.Thread(target=self._scan_adf)
        thread.start()
        return thread

    def scan_manual_duplex(self, event=None):
        self.PushStatusText("Manually duplexing pages from ADF.")
        self.frame.config.Write('/Scan/Source', 'Manual Duplex')
        self.pages = []
        thread = threading.Thread(target=self._scan_adf)
        thread.start()
        return thread

    def scan_adf(self, event=None):
        self.PushStatusText("Scanning fronts from ADF.")
        self.frame.config.Write('/Scan/Source', 'ADF')
        self.pages = []
        thread = threading.Thread(target=self._scan_adf)
        thread.start()
        return thread

    def receive_pages_from_adf(self, pages):
        if pages:
            if self.pages:
                self.pages = [j for i in zip(self.pages, reversed(pages)) for j in i]
                self.frame.library.import_images(self.pages)
                self.pages = []
                self.PopStatusText()
            else:
                self.pages.extend(pages)
                if self.frame.config.Read('/Scan/Source', '') == 'Manual Duplex':
                    wx.MessageDialog(self.frame,
                                     '',
                                     'Load the stack face-down back into the ADF',
                                     wx.OK).ShowModal()
                    threading.Thread(target=self._scan_adf).start()
                else:
                    self.frame.library.import_images(self.pages)
                    self.pages = []
                    self.PopStatusText()
        else:
            answer = wx.MessageBox("Please load the document into the ADF.", "", wx.OK|wx.CANCEL)
            if answer == wx.OK:
                threading.Thread(target=self._scan_adf).start()

    def _scan_adf(self):
        source = self.frame.config.Read('/Scan/Source', 'ADF')
        wx.LogDebug(f'Scan Source: {source}')
        self.device.source = 'ADF' if source == 'Manual Duplex' else source
        self.device.br_x = self.device.opt['br_x'].constraint[1]  # X_max
        self.device.br_y = self.device.opt['br_y'].constraint[1]  # Y_max
        # wx.LogDebug(self.device.__dict__)
        try:
            pages = list(self.device.multi_scan())
            wx.CallAfter(self.receive_pages_from_adf, pages)
        except sane._sane.error as e:
            wx.LogWarning(repr(e))
            self.PopStatusText()

    def scan_one_from_flatbed(self, event=None):
        self.PushStatusText("Scanning one page from flatbed.")
        thread = threading.Thread(target=self._scan_one_from_flatbed)
        thread.start()
        return thread

    def _scan_one_from_flatbed(self):
        self.device.resolution = int(self.frame.config.Read('/Scan/Resolution'))
        self.device.source = 'Flatbed'
        self.device.mode = 'color'
        image = self.scan()
        self.PopStatusText()
        self.frame.library.import_image(image)

    def scan_multiple_from_flatbed(self, event=None):
        self.PushStatusText("Scanning multiple pages from flatbed.")
        self.pages = []
        thread = threading.Thread(target=self._scan_one_of_multiple)
        thread.start()
        return thread

    def receive_one_of_multiple(self, page):
        self.pages.append(page)
        dialog = wx.MessageDialog(self.frame, "", f"Scanned Page {len(self.pages)}", wx.YES_NO)
        dialog.SetYesNoLabels("Scan Another Page", "All Done")
        result = dialog.ShowModal()
        if result == wx.ID_YES:
            threading.Thread(target=self._scan_one_of_multiple).start()
        else:
            self.PopStatusText()
            self.frame.library.import_images(self.pages)
            self.pages = []

    def _scan_one_of_multiple(self, event=None):
        wx.LogDebug('Scanner._scan_multiple_from_flatbed(): START')
        self.device.source = 'Flatbed'
        page = self.scan()
        wx.CallAfter(self.receive_one_of_multiple, page)
