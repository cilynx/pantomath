from .image import Image


class Original():
    def __init__(self, pages):
        if isinstance(pages[0], Image):
            self.pages = pages
        else:
            self.pages = [Image(page) for page in pages]

    @property
    def ext(self):
        if isinstance(self.pages[0], Image):
            return '.tiff'
        else:
            raise ValueError(f"Don't know extension for {self.pages[0]}")

    def save(self, filepath):
        print(f'Original.save({filepath})')
        if isinstance(self.pages[0], Image):
            print(f'Original.save(): Saving {self.pages}')
            self.pages[0].save(filepath,
                               compression='lzma',
                               lossless=True,
                               save_all=True,
                               append_images=self.pages[1:])
        else:
            raise ValueError(f"Don't know how to save {self.pages}")
        print('Original.save(END)')
