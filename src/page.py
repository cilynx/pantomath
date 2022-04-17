from .placeable import Placeable


class Page(Placeable):
    def __init__(self, document, left, top, width, height, confidence, text):
        super().__init__(left, top, width, height)
        if text:
            raise Exception(f'Page should never be passed text directly: {text}')
        self.document = document
        self.blocks = []

    ###########################################################################
    # Properties
    ###########################################################################

    @property
    def paragraphs(self):
        return [paragraph for block in self.blocks for paragraph in block.paragraphs]

    @property
    def lines(self):
        return [line for paragraph in self.paragraphs for line in paragraph.lines]

    @property
    def words(self):
        return [word for line in self.lines for word in line.words]
