import wx


class Organizations(wx.Panel):
    """
    The Organizations UI
    """

    def __init__(self, parent):
        super().__init__(parent)
        self.parent = parent
        t = wx.StaticText(self, -1, "This is the second tab", (20,20))
