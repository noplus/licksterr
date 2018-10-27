import logging

from licksterr.analyzer import parse_song
from licksterr.models import Form, Scale, Note, Measure, NOTES_DICT, FormMeasure, Beat
from tests import LicksterrTest

logger = logging.getLogger(__name__)

class TestDatabase(LicksterrTest):
    def test_db_init(self):
        notes = Note.query.all()
        forms = Form.query.all()
        self.assertEqual(6 * 30, len(notes))
        self.assertEqual(len(Scale) * 12 * 5, len(forms))

    def test_song_parsing(self):
        parse_song("tests/test.gp5")
        # two identical measures should produce a single row in the database
        self.assertEqual(1, len(Measure.query.all()))
        # only 4 beats should be generated
        self.assertEqual(4, len(Beat.query.all()))
        m = Measure.query.first()
        # There should be a 100% match with the E form of the G major scale
        self._test_form_match(1, 'G', Scale.IONIAN, 'E', m)
        # There should be a 75% match with the E form of the G major pentatonic (no 4th)
        self._test_form_match(0.75, 'G', Scale.MAJORPENTATONIC, 'E', m)

    def _test_form_match(self, expected, key, scale, form, measure):
        form = Form.get(NOTES_DICT[key], scale, form)
        match = FormMeasure.get(form, measure).match
        self.assertEqual(expected, match)
