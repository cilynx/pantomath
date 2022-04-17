from .placeable import Placeable


class BagOfWords(Placeable):
    def __init__(self, words):
        self.words = words

    ###########################################################################
    # Properties
    ###########################################################################

    @property
    def left(self):
        # Leftmost edge of all Words in the Bag
        return min([word.left for word in self.words])

    @property
    def top(self):
        # Highest top of all Words in the Bag
        return min([word.top for word in self.words])

    @property
    def width(self):
        # Right - Left.  It's messy because Tesseract wants L,T,W,H
        #                to be declared while R and B are derived.
        return max([word.right for word in self.words]) - self.left

    @property
    def height(self):
        # Bottom - Top.  It's messy because Tesseract wants L,T,W,H
        #                to be declared while R and B are derived.
        return max([word.bottom for word in self.words]) - self.top

    @property
    def text(self):
        return ' '.join([word.text for word in self.words])

    @property
    def last_word(self):
        return self.words[-1]

    @property
    def first_word(self):
        return self.words[0]
