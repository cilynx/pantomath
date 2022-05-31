class Placeable:
    def __init__(self, left, top, width, height):
        # wx.LogDebug(f'{type(self)}.__init__{left, top, width, height}')
        self.left = left
        self.top = top
        self.width = width
        self.height = height

    ###########################################################################
    # Properties
    ###########################################################################

    @property
    def right(self):
        return self.left + self.width

    @property
    def center(self):
        return (self.right - self.left)/2

    @property
    def bottom(self):
        return self.top + self.height

    @property
    def middle(self):
        return (self.top + self.bottom)/2

    ###########################################################################
    # Public Methods
    ###########################################################################

    def x_space_between(self, placeable):
        # Rightmost Left - Leftmost Right
        return max([self.left, placeable.left]) - min([self.right, placeable.right])

    def y_space_between(self, placeable):
        # Highest Bottom - Lowest Top
        return min([self.bottom, placeable.bottom]) - max([self.top, placeable.top])

    def next_to(self, placeable):
        # TODO: Not sure I like the Line requirement here.
        #       Spatial v-align might be a more versatile test.
        if self.text == 'access' and placeable.text == 'network':
            wx.LogDebug(f'|{self.x_space_between(placeable)}|{self.height}|{placeable.height}|')
        if self.line != placeable.line:
            return False
        return self.x_space_between(placeable) < 2 * self.height

    def left_aligned(self, placeable):
        # Left edges are within one average letter space of each other
        return abs(placeable.left - self.left) < self.width / len(self.text)

    def right_aligned(self, placeable):
        # Left edges are within one average letter space of each other
        return abs(placeable.right - self.right) < self.width / len(self.text)

    def center_aligned(self, placeable):
        # H-Centers are within one average letter space of each other
        return abs(placeable.center - self.center) < self.width / len(self.text)

    def aligned_with(self, placeable):
        # Self is H-Aligned with Placeable in any possible way
        if self.left_aligned(placeable):
            wx.LogDebug("left_aligned")
            return 'left'
        if self.right_aligned(placeable):
            wx.LogDebug("right_aligned")
            return 'right'
        if self.center_aligned(placeable):
            wx.LogDebug("center_aligned")
            return 'center'
        return False

    def just_below(self, placeable):
        if self.page == placeable.page:
            # Self's top is within Self's height of Placeable's bottom
            return 0 < self.top - placeable.bottom < self.height
        # elif self.page.num == placeable.page.num + 1:
        #     # TODO: Support flowing onto the next page
        #     return False
        else:
            return False
