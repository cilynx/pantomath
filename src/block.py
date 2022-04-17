from .placeable import Placeable


class Block(Placeable):
    def __init__(self, page, left, top, width, height, confidence, text):
        super().__init__(left, top, width, height)
        if text:
            raise Exception(f'Block should never be passed text directly: {text}')
        self.page = page
        self.paragraphs = []

    ###########################################################################
    # Properties
    ###########################################################################

    @property
    def lines(self):
        return [line for paragraph in self.paragraphs for line in paragraph.lines]

    @property
    def words(self):
        return [word for line in self.lines for word in line.words]
