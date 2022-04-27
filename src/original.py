import os
import shutil
import filetype
import pdf2image

from .image import Image


class Original():
    def __init__(self, pages):
        self.original_path = None
        if isinstance(pages, str):
            if os.path.isfile(pages):
                self.original_path = pages
                kind = filetype.guess(pages)
                if not kind:
                    raise ValueError("Unknown filetype.")
                elif kind.mime.endswith('/pdf'):
                    self.pages = [Image(page) for page in pdf2image.convert_from_path(pages)]
        elif isinstance(pages[0], Image):
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
        if self.original_path:
            ext = os.path.splitext(self.original_path)[1]
            dir = os.path.dirname(filepath)
            dest = os.path.join(dir, 'original.' + ext)
            shutil.move(self.original_path, dest)
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
