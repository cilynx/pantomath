import wx


class Config(wx.Config):

    def __init__(self, name):
        super().__init__(name)

    def Read(self, *args):
        wx.LogDebug(f"Config.Read({args}) = {super().Read(*args)}")
        return super().Read(*args)

    def Write(self, *args):
        wx.LogDebug(f"Config.Write({args})")
        result = super().Write(*args)
        super().Flush()
        return result

    def DefaultTo(self, *args):
        wx.LogDebug(f"Config.DefaultTo({args})")
        if not super().Read(args[0]):
            result = super().Write(*args)
            super().Flush()
            return result
        else:
            wx.LogDebug(f'Already set -- not clobbering')

    def ReadBool(self, *args):
        wx.LogDebug(f"Config.ReadBool({args})")
        return super().ReadBool(*args)

    def WriteBool(self, *args):
        wx.LogDebug(f"Config.WriteBool({args})")
        result = super().WriteBool(*args)
        super().Flush()
        return result
