import wx


class Documents(wx.Panel):
    """
    The Documents UI
    """

    def __init__(self, parent):
        super().__init__(parent)
        self.parent = parent
        t = wx.StaticText(self, -1, "This is the first tab", (20,20))
