import wx


class Documents(wx.Panel):
    """
    The Documents UI
    """

    def __init__(self, parent):
        wx.LogDebug('Initializing Documents Tab')
        super().__init__(parent)
        self.parent = parent
        self.library = parent.Parent.Parent.library
        self.notebook = wx.Listbook(self, wx.ID_ANY, style=wx.BK_LEFT)
        pages = [(wx.Panel(self, wx.ID_ANY), "Panel One"),
                 (wx.Panel(self, wx.ID_ANY), "Panel Two"),
                 (wx.Panel(self, wx.ID_ANY), "Panel Three")]
        pages = [(wx.Panel(self, wx.ID_ANY), doc) for doc in self.library.documents()]
        for page, label in pages:
            wx.LogDebug('Adding Document to UX')
            self.notebook.AddPage(page, label)
        sizer = wx.BoxSizer(wx.VERTICAL)
        sizer.Add(self.notebook, 1, wx.EXPAND)
        self.SetSizer(sizer)

        self.Bind(wx.EVT_LISTBOOK_PAGE_CHANGED, self.OnPageChanged)
        self.Bind(wx.EVT_LISTBOOK_PAGE_CHANGING, self.OnPageChanging)

    def OnPageChanged(self, event):
        old = event.GetOldSelection()
        new = event.GetSelection()
        sel = self.notebook.GetSelection()
        print('OnPageChanged,  old:%d, new:%d, sel:%d\n' % (old, new, sel))
        event.Skip()

    def OnPageChanging(self, event):
        old = event.GetOldSelection()
        new = event.GetSelection()
        sel = self.GetSelection()
        print('OnPageChanging, old:%d, new:%d, sel:%d\n' % (old, new, sel))
        event.Skip()
