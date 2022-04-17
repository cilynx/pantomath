from .placeable import Placeable


class Paragraph(Placeable):
    def __init__(self, block, left, top, width, height, confidence, text):
        super().__init__(left, top, width, height)
        if text:
            raise Exception(f'Paragraph should never be passed text directly: {text}')
        self.block = block
        self.lines = []

    ###########################################################################
    # Properties
    ###########################################################################

    @property
    def text(self):
        return ' '.join([line.text for line in self.lines])

    @property
    def words(self):
        return [word for line in self.lines for word in line.words]
