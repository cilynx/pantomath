import PIL.Image
import types

from PIL import ImageOps, ImageFilter
from itertools import chain, product
from functools import partial


class Image():

    def __init__(self, arg):

        self._skew = None
        self._bbox = None

        if isinstance(arg, str):
            self.pil_image = PIL.Image.open(arg)
        elif isinstance(arg, PIL.Image.Image):
            self.pil_image = arg
        else:
            raise Exception(f"Don't know what to do with {arg}")

        if self.pil_image.mode == 'RGBA':
            opaque = PIL.Image.new("RGB", self.pil_image.size, (255, 255, 255))
            opaque.paste(self.pil_image, mask=self.pil_image.split()[3])
            self.pil_image = opaque

    ###########################################################################
    # Send anything we don't recognize through to PIL
    ###########################################################################

    def __getattr__(self, name):
        # Surface PIL.ImageOps as chainable Image methods
        if hasattr(ImageOps, name):
            return partial(self._ImageOps, name)
        # Wrap PIL.Image methods
        elif hasattr(self.pil_image, name):
            if isinstance(self.pil_image.__getattribute__(name),
                          types.MethodType):
                return partial(self._Image, name)
            else:
                return self.pil_image.__getattribute__(name)
        else:
            raise Exception(f"Don't know how to handle {name}")

    ###########################################################################
    # Wrappers
    ###########################################################################

    def _Image(self, name, *args, **kwargs):
        # print(f"_Image(): {self.pil_image} {name} {args} {kwargs}")
        Op = self.pil_image.__getattribute__(name)
        result = Op(*args, **kwargs)
        # print(result)
        if type(result) is PIL.Image.Image:
            return Image(result)
        elif result is None and name in ['show']:
            return self
        else:
            return result

    def _ImageOps(self, name, *args, **kwargs):
        ImageOp = ImageOps.__getattribute__(name)
        return Image(ImageOp(self.pil_image, *args, **kwargs))

    ###########################################################################
    # Simple binary threshold
    ###########################################################################

    def threshold(self, thresh=127):
        return Image(self.pil_image.point(lambda p: 255 if p > thresh else 0))

    ###########################################################################
    # Chainable thumbnail()
    ###########################################################################

    def thumbnail(self, size=(200, 200)):
        copy = self.pil_image.copy()
        copy.thumbnail(size)
        return Image(copy)

    ###########################################################################
    # Contiguous Areas: Letters, Pictures, Lines, etc.
    ###########################################################################

    def regions(self, test):
        pixel = self.pil_image.load()
        print("&&&&&&&&&&&&&&&&&&&&&", self.pil_image.size)
        xs, ys = map(range, self.pil_image.size)
        pixels = set(xy for xy in product(xs, ys) if test(pixel[xy]))
        while pixels:
            region = set()
            edge = set([pixels.pop()])
            while edge:
                region |= edge
                pixels -= edge
                edge = pixels.intersection(
                    chain.from_iterable(((x-1,y),(x,y-1),(x+1,y),(x,y+1)) for x,y in edge)
                )
            yield Region(region)

    def test(self, pixel):
        r, g, b = pixel
        return r < 10 and g < 10 and b < 10

    ###########################################################################
    # Skew & Bounding Box
    ###########################################################################

    def skew(self):
        print(f'Skew: {self._skew}, BBox: {self._bbox}')
        if self._skew is None:
            self._skew, self._bbox = self.get_skew_and_bbox()
            print(f'Skew: {self._skew}, BBox: {self._bbox}')
        return self._skew

    def bbox(self):
        print(f'BBox: {self._bbox}, Skew: {self._skew}')
        if self._bbox is None:
            self._skew, self._bbox = self.get_skew_and_bbox()
            print(f'Skew: {self._skew}, BBox: {self._bbox}')
        return self._bbox

    def get_skew_and_bbox(self, minimum=-45, maximum=45, step=1):
        guess = 0
        dir = 1

        # image = self.crop(20).filter(ImageFilter.GaussianBlur(1)).threshold(210)
        # regions = image.regions(image.test)
        # draw = ImageDraw.Draw(image.pil_image)
        # for region in regions:
        #     if region.bigger_than(5):
        #         draw.rectangle(region.bbox(), outline=(255, 0, 0))
        #         print(region.bbox())
        # image.show()
        # return

        image = self.crop(20).filter(ImageFilter.GaussianBlur(10)).threshold(210)
        orig_image = self.crop(20).thumbnail((400, 400)).filter(ImageFilter.GaussianBlur(1))
        orig_image = orig_image.threshold(210)
        orig_image = orig_image.invert()
        orig_image = orig_image.filter(ImageFilter.MaxFilter(3))
        orig_image = orig_image.filter(ImageFilter.MaxFilter(3))
        left, upper, right, lower = orig_image.getbbox()
        prev_area = (lower-upper)*(right-left)
        equal_count = 0
        # print(min, guess, max, prev_area, lower, upper, right, left)
        while minimum <= guess <= maximum:
            guess += step*dir
            image = orig_image.rotate(guess)
            bbox = image.getbbox()
            # draw = ImageDraw.Draw(image.pil_image)
            # draw.rectangle(image.getbbox(), outline=(0, 255, 0))
            # image.show()
            # (Lower - Upper) * (Right - Left)
            area = (bbox[3]-bbox[1])*(bbox[2]-bbox[0])
            # print(min, guess, max, area, prev_area, lower, upper, right, left)
            if area > prev_area:
                if equal_count:
                    angle = guess - dir*step*equal_count/2
                    # print(f'################################################ {self.size}')
                    bbox = [i * max(self.size) / 400 for i in bbox]
                    return angle, bbox
                dir *= -1
                step *= 1/2
            elif area == prev_area:
                equal_count += 1
            prev_area = area
        return 0

    def deskew(self, minimum=-45, maximum=45, step=1):
        image = self.rotate(self.skew())
        image._bbox = self.bbox()
        return image

    def autocrop(self):
        return self.pil_image.crop(self.bbox())


class Region():
    def __init__(self, pixels):
        self.pixels = pixels
        self._bbox = None

    def bbox(self):
        if self._bbox is None:
            xs, ys = zip(*self.pixels)
            self._bbox = min(xs), min(ys), max(xs), max(ys)
        return self._bbox

    def wider_than(self, width):
        bbox = self.bbox()
        return bbox[2]-bbox[0] > width

    def taller_than(self, height):
        bbox = self.bbox()
        return bbox[3]-bbox[1] > height

    def bigger_than(self, dim):
        return self.wider_than(dim) or self.taller_than(dim)
