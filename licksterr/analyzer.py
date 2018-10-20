import json
import os
from collections import defaultdict
from pathlib import Path

from mingus.core import notes

from licksterr.guitar import Chord
from licksterr.models import Form, Lick

PROJECT_ROOT = Path(os.path.realpath(__file__)).parents[1]
ASSETS_DIR = PROJECT_ROOT / "assets"
ANALYSIS_FOLDER = os.path.join(ASSETS_DIR, "analysis")
FORMS_DB = os.path.join(ANALYSIS_FOLDER, "forms.json")


class Parser:
    def __init__(self, formsfile=FORMS_DB):
        self.note_forms_map = defaultdict(set)  # note: {set of forms that contain this note}
        self.all_forms = set()
        with open(formsfile) as f:
            self.forms_db = json.loads(f.read())  # key: {scale: {form: Form}}
        # Parse forms database and initialize utility objects
        for key, scale_dict in self.forms_db.items():
            for scale, form_dict in scale_dict.items():
                for form in form_dict.keys():
                    notes_list = tuple((string, fret) for string, fret in self.forms_db[key][scale][form])
                    f = Form(notes_list, key, scale, form)
                    self.forms_db[key][scale][form] = f
                    self.all_forms.add(f)
                    for note in notes_list:
                        self.note_forms_map[note].add(f)
        # Mutable objects for analysis
        self.forms_result = defaultdict(list)  # form: [list of licks contained in this form]
        self.chords_result = []
        self.current_notes = []
        self.possible_forms = None
        self.notes_result = defaultdict(int)  # note: number of time this note is played

    def parse_song(self, song):
        for guitar_track in song.guitars:
            self.parse_track(guitar_track)

    def parse_track(self, guitar_track):
        start, end = 1, None
        self.current_notes = []
        self.possible_forms = self.all_forms.copy()
        pause_duration = 0
        for i, measure in enumerate(guitar_track.measures, start=1):
            end = i
            for beat in measure.beats:
                if not beat.notes:
                    pause_duration += beat.duration
                    if pause_duration >= measure.duration and self.current_notes:
                        self.insert_lick(start, end)
                        start = i
                    continue
                pause_duration = 0
                if beat.chord:
                    self.insert_lick(start, end)
                    start = i
                    self.chords_result.append(Chord(beat.chord))
                else:
                    for note in beat.notes:
                        self.possible_forms.intersection_update(self.note_forms_map[note])
                        self.current_notes.append(note)
                        self.notes_result[note] += 1
        self.insert_lick(start, end)

    def insert_lick(self, start, end):
        if not self.current_notes:
            return
        lick = Lick(self.current_notes, start=start, end=end)
        matching_forms = {form for form in self.possible_forms if form.contains(lick)}
        for form in matching_forms:
            self.forms_result[form].append(lick)
        self.possible_forms = self.all_forms.copy()
        self.current_notes.clear()

    def get_likely_keys(self):
        """Returns a list of integers representing the int values of the notes that were played the most"""
        result = defaultdict(int)
        for note, played in self.notes_result.items():
            result[notes.note_to_int(note.name)] += played
        return sorted(result.values(), key=result.get)

    def reset(self):
        self.forms_result.clear()
        self.notes_result.clear()
        self.chords_result.clear()


if __name__ == '__main__':
    pass
