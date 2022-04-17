from .placeable import Placeable


class Line(Placeable):
    def __init__(self, paragraph, left, top, width, height, confidence, text):
        super().__init__(left, top, width, height)
        if text:
            raise Exception(f'Line should never be passed text directly: {text}')
        self.paragraph = paragraph
        self.words = []
        self.breaks = []

    ###########################################################################
    # Properties
    ###########################################################################

    @property
    def text(self):
        return ' '.join([word.text for word in self.words])

    @property
    def prev(self):
        index = self.paragraph.lines.index(self)
        if index:
            return self.paragraph.lines[index-1]

    ###########################################################################
    # Public Methods
    ###########################################################################

    def append(self, word):
        self.words.append(word)
        self.breaks.extend([word.left, word.right])
