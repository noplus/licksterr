import os

from PIL import Image, ImageColor

from src import ASSETS_FOLDER
from src.guitar import Guitar


class GuitarImage(Guitar):
    def __init__(self):
        super().__init__()
        self.im = Image.open(os.path.join(ASSETS_FOLDER, "blank_fret_board.png"))
        # The open high E string circle is at (19,15). H step: 27px. V step: 16px. 22 frets total + open strings
        for i, string in self.strings.items():
            string.positions = tuple((19 + j * 27, 15 + (i - 1) * 16) for j, note in enumerate(string.notes))

    def fill_circle(self, xy, color=None, im=None):
        """Fills the area around the dot until it founds the borders"""
        color = color if color else ImageColor.getcolor('green', mode='RGBA')
        black = ImageColor.getcolor('black', mode='RGBA')
        im = im if im else self.im
        pixel = im.getpixel(xy)
        if pixel not in (black, color):  # skips if black or already filled
            im.putpixel(xy, color)
            for ij in (1, 0), (0, 1), (-1, 0), (0, -1):  # goes to adjacent pixels
                new_xy = (xy[0]+ij[0], xy[1]+ij[1])
                self.fill_circle(new_xy, color, im)
        return im


def main():
    pass


if __name__ == '__main__':
    main()
