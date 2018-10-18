import os
import unittest

from PIL import ImageColor

from cagedfinder.image import GuitarImage
from tests import TEST_ASSETS


class TestImage(unittest.TestCase):
    FORMS = 'CAGED'

    @classmethod
    def setUpClass(cls):
        cls.guitar = GuitarImage()

    def test_fill(self):
        """Should produce an image with all circles filled in the standard color and E notes in red"""
        im = self.guitar.im.copy()
        for string in self.guitar.strings:
            for note in string.notes:
                color = 'red' if note.name == 'E' else 'green'
                self.guitar.fill_note(note, ImageColor.getcolor(color, mode='RGBA'), im=im)
        im.save(os.path.join(TEST_ASSETS, "test_fill.png"))
