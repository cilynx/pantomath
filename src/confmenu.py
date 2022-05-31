import wx


class ConfMenu(wx.Menu):

    def __init__(self, frame, prefix):

        super().__init__()
        self.frame = frame
        self.prefix = prefix

    def AppendRadioSet(self, *args, **kwargs):

        def handler(event):
            for item in args:
                if event.GetId() == item['obj'].GetId():
                    wx.LogDebug(f"Writing {self.prefix}/{kwargs['confKey']}: {item['confValue']}")
                    self.frame.config.Write(f"{self.prefix}/{kwargs['confKey']}", item['confValue'])
                    self.frame.SetStatusText(f"{self.prefix.replace('/','')} {kwargs['confKey']} is now {item['confValue']}", 1)

        for item in args:
            item['obj'] = self.AppendRadioItem(wx.ID_ANY, item['shortHelp'], item['longHelp'])
            self.frame.Bind(wx.EVT_MENU, handler, item['obj'])

        for item in args:
            if self.frame.config.Read(f"{self.prefix}/{kwargs['confKey']}") == item['confValue']:
                wx.LogDebug(f"Read {self.prefix}/{kwargs['confKey']}: {item['confValue']}")
                self.Check(item['obj'].GetId(), True)
