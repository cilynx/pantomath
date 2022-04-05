import wx
import sane
import threading


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
    # Blocking Functions: All _functions would block the UI if
    #                     not dispatched in separate threads
    ###########################################################################

    def _init_scanner(self):
        self.sane_version = sane.init()
        self.devname, self.vendor, self.model, self.type = sane.get_devices()[0]
        self.device = sane.open(self.devname)
        self.PushStatusText(self.model + " Ready")
        self.frame.EnableScanUI()

    def scan_all_from_adf(self, event=None):
        self.PushStatusText("Scanning all pages from ADF.")
        thread = threading.Thread(target=self._scan_all_from_adf)
        thread.start()
        return thread

    def _scan_all_from_adf(self):
        self.device.source = 'ADF'
        self.br_x = 0
        self.br_y = 0
        images = list(self.device.multi_scan())
        if images:
            images[0].save('out.pdf', save_all=True, append_images=images[1:])
            images[0].show()
        else:
            wx.MessageBox("Is the document loaded in the ADF?")
        self.PopStatusText()

    def scan_one_from_flatbed(self, event=None):
        self.PushStatusText("Scanning one page from flatbed.")
        thread = threading.Thread(target=self._scan_one_from_flatbed)
        thread.start()
        return thread

    def _scan_one_from_flatbed(self):
        self.device.source = 'Flatbed'
        self.scan().show()
        self.PopStatusText()

    def scan_multiple_from_flatbed(self, event=None):
        self.PushStatusText("Scanning multiple pages from flatbed.")
        thread = threading.Thread(target=self._scan_multiple_from_flatbed)
        thread.start()
        return thread

    def _scan_multiple_from_flatbed(self):
        self.device.source = 'Flatbed'
        i = 1
        while True:
            self.scan().show()
            dialog = wx.MessageDialog(self.frame, "", f"Scanned Page {i}", wx.YES_NO)
            dialog.SetYesNoLabels("Scan Another Page", "All Done")
            result = dialog.ShowModal()
            if result != wx.ID_YES:
                break
            i += 1
        self.PopStatusText()
