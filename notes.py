from os import mkdir
from os.path import dirname, abspath, isfile, join, exists, splitext

NOTES_CYCLE_FLATS = ["c", "db", "d", "eb", "e", "f", "gb", "g", "ab", "a", "bb", "b"]
NOTES_CYCLE_SHARPS = ["c", "c#", "d", "d#", "e", "f", "f#", "g", "g#", "a", "a#", "b"]
#REF_NOTES = NOTES_CYCLE_FLATS
REF_NOTES = NOTES_CYCLE_SHARPS

"""
Formats used for an example note: middle C.
    1st format: midi note name
        C5; range: C0 -> G10
    2nd format: midi value
        60, range: 0 -> 127
    3rd format: Humdrum
        c, range: CCCC -> gggggg
"""


class Note(object):
    def __init__(self, midi_note_value, ref_notes=REF_NOTES):
        self.midi_value = midi_note_value
        self.octave = self.midi_value // 12
        note_idx = self.midi_value - self.octave*12
        self.note_name = ref_notes[note_idx]
        self.note_unaltered = self.note_name[0]
        if len(self.note_name) > 1:
            self.alteration = self.note_name[1]
        else:
            self.alteration = ""

        if self.octave < 5:
            self.humdrum = self.note_unaltered.upper() * (5 - self.octave)\
                + self.alteration
        else:
            self.humdrum = self.note_unaltered * (self.octave - 4)\
                + self.alteration

    def __str__(self):
        s_out = f"{self.midi_value} | {self.note_name}{self.octave} | " +\
            f"{self.humdrum}"
        return s_out

    def name_octave(self):
        return f"{self.note_name}{self.octave}"

    def upper(self):
        return self.note_unaltered.upper() + self.alteration


ALL_NOTES_FLATS = [Note(i, ref_notes=NOTES_CYCLE_FLATS) for i in range(128)]
ALL_NOTES_SHARPS = [Note(i, ref_notes=NOTES_CYCLE_SHARPS) for i in range(128)]


def note_humdrum_to_note_element(note_humdrum):
    for ref in [ALL_NOTES_FLATS, ALL_NOTES_SHARPS]:
        for note in ref:
            if note_humdrum == note.humdrum:
                return note

    print(note_humdrum)
    assert(False), f"Note not found: {note_humdrum}"

