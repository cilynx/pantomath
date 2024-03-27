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
        self.deviceMenu = ConfMenu(self.frame, "/Scan")
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

    def ReplaceStatusText(self, text):
        self.PopStatusText()
        self.PushStatusText(text)

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
                    scanners = [{'shortHelp': device[2], 'longHelp': device[0], 'confValue': device[0]} for device in devices]
                    self.deviceMenu.AppendRadioSet(*scanners, confKey="Device")

                    if configured_devname := self.frame.config.Read('/Scan/Device', ''):
                        for device in devices:
                            if device[0] == configured_devname:
                                break
                        else:
                            self.frame.config.Write('/Scan/Device', device[0])
                    else:
                        self.frame.config.Write('/Scan/Device', devices[0][0])
                    self.device = sane.open(self.frame.config.Read('/Scan/Device'))
                    wx.CallAfter(self.PushStatusText, self.frame.config.Read('/Scan/Device') + " Ready")
                    wx.LogDebug('Enabling Scan UI')
                    for option in self.device.get_options():
                        wx.LogDebug(f'Option: {option}')
                        self.options[option[1]] = option[8]
                    self.device.close()
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
        self.PushStatusText("Scanning fronts from ADF.")
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
                self.PushStatusText("Processing scanned images")
                self.frame.library.import_images(self.pages)
                self.PopStatusText()
                self.pages = []
                self.PopStatusText()
            else:
                self.pages.extend(pages)
                if self.frame.config.Read('/Scan/Source', '') == 'Manual Duplex':
                    self.ReplaceStatusText("Waiting for stack flip.")
                    wx.MessageDialog(self.frame,
                                     '',
                                     'Load the stack face-down back into the ADF',
                                     wx.OK).ShowModal()
                    self.ReplaceStatusText("Scanning backs from ADF.")
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
        self.device = sane.open(self.frame.config.Read('/Scan/Device'))
        source = self.frame.config.Read('/Scan/Source', 'ADF')
        wx.LogDebug(f'Scan Source: {source}')
        self.device.source = 'ADF' if source == 'Manual Duplex' else source
        self.device.mode = self.frame.config.Read('/Scan/Mode')
        self.device.resolution = int(self.frame.config.Read('/Scan/Resolution'))
        self.device.br_x = self.device.opt['br_x'].constraint[1]  # X_max
        self.device.br_y = self.device.opt['br_y'].constraint[1]  # Y_max
        # wx.LogDebug(self.device.__dict__)
        try:
            pages = list(self.device.multi_scan())
            self.device.close()
            wx.CallAfter(self.receive_pages_from_adf, pages)
        except sane._sane.error as e:
            self.device.close()
            wx.LogWarning(repr(e))
            self.PopStatusText()

    def scan_one_from_flatbed(self, event=None):
        self.PushStatusText("Scanning one page from flatbed.")
        thread = threading.Thread(target=self._scan_one_from_flatbed)
        thread.start()
        return thread

    def _scan_one_from_flatbed(self):
        self.device = sane.open(self.frame.config.Read('/Scan/Device'))
        self.device.source = 'Flatbed'
        self.device.mode = self.frame.config.Read('/Scan/Mode')
        self.device.resolution = int(self.frame.config.Read('/Scan/Resolution'))
        while True:
            try:
                wx.LogDebug(self.device.source)
                wx.LogDebug(self.device.mode)
                wx.LogDebug(str(self.device.resolution))
                image = self.scan()
                self.device.close()
                break
            except sane._sane.error as e:
                self.device.close()
                wx.LogVerbose(repr(e))
        self.ReplaceStatusText("Processing scanned images")
        self.frame.library.import_image(image)
        self.PopStatusText()

    def scan_multiple_from_flatbed(self, event=None):
        self.PushStatusText("Scanning Page 1 from flatbed.")
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
            self.ReplaceStatusText(f"Scanning page {len(self.pages)+1} from flatbed")
            threading.Thread(target=self._scan_one_of_multiple).start()
        else:
            self.ReplaceStatusText("Processing scanned images")
            self.frame.library.import_images(self.pages)
            self.PopStatusText()
            self.pages = []

    def _scan_one_of_multiple(self, event=None):
        wx.LogDebug('Scanner._scan_multiple_from_flatbed(): START')
        self.device = sane.open(self.frame.config.Read('/Scan/Device'))
        self.device.source = 'Flatbed'
        self.device.mode = self.frame.config.Read('/Scan/Mode')
        self.device.resolution = int(self.frame.config.Read('/Scan/Resolution'))
        page = self.scan()
        self.device.close()
        wx.CallAfter(self.receive_one_of_multiple, page)
