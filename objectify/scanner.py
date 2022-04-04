import sane


class Scanner():
    """
    A simple Scanner object
    """

    def __init__(self):
        self.sane_version = sane.init()
        self.uri, self.make, self.model, self.modes = sane.get_devices()[0]
        self.device = sane.open(self.uri)

    def __getattr__(self, name):
        return self.device.__getattribute__(name)

    def get_pil_image(self):
        """
        Start a scan and return a PIL.Image

        :returns: A PIL.Image
        """
        self.start()
        return self.snap()
