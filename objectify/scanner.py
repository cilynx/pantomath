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
        self.devname, self.vendor, self.model, self.type = sane.get_devices()[0]
        self.device = sane.open(self.devname)
        self.PushStatusText(self.model + " Ready")
        wx.LogDebug('Enabling Scan UI')
        self.frame.EnableScanUI()

    def scan_hardware_duplex(self, event=None):
        self.PushStatusText("Scanning pages from ADF hardware duplexer.")
        thread = threading.Thread(target=self._scan_adf, args=('ADF Duplex',))
        thread.start()
        return thread

    def scan_manual_duplex(self, event=None):
        self.PushStatusText("Manually duplexing pages from ADF.")
        thread = threading.Thread(target=self._scan_adf, args=('ADF', True))
        thread.start()
        return thread

    def scan_adf(self, event=None):
        self.PushStatusText("Scanning fronts from ADF.")
        thread = threading.Thread(target=self._scan_adf)
        thread.start()
        return thread

    def _scan_adf(self, source='ADF', manual_duplex=False):
        self.device.resolution = int(self.frame.config.Read('/Scan/Resolution'))
        self.device.source = source
        self.device.br_x = self.device.opt['br_x'].constraint[1]  # X_max
        self.device.br_y = self.device.opt['br_y'].constraint[1]  # Y_max
        # print(self.device.__dict__)
        images = list(self.device.multi_scan())
        if manual_duplex:
            wx.MessageDialog(self.frame,
                             '',
                             'Load the stack face-down back into the ADF',
                             wx.OK).ShowModal()
            backs = list(self.device.multi_scan())
            images = [j for i in zip(images, reversed(backs)) for j in i]
        if images:
            images[0].save('out.pdf', save_all=True, append_images=images[1:])
        else:
            wx.MessageBox("Is the document loaded in the ADF?")
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
        self.frame.ImportImage(image)

    def scan_multiple_from_flatbed(self, event=None):
        self.PushStatusText("Scanning multiple pages from flatbed.")
        thread = threading.Thread(target=self._scan_multiple_from_flatbed)
        thread.start()
        return thread

    def _scan_multiple_from_flatbed(self):
        self.device.source = 'Flatbed'
        images = []
        while True:
            images.append(self.scan())
            dialog = wx.MessageDialog(self.frame, "", f"Scanned Page {len(images)}", wx.YES_NO)
            dialog.SetYesNoLabels("Scan Another Page", "All Done")
            result = dialog.ShowModal()
            if result != wx.ID_YES:
                break
        if images:
            images[0].save('out.pdf', save_all=True, append_images=images[1:])
        self.PopStatusText()
