import re
from pychord import Chord


def create_pychord_objects(song_keys, chord_progressions):
    pychord_song_keys = []
    pychord_chord_progressions = []

    for i in range(len(song_keys)):  # convert strings in the song_keys list to pychord objects
        song_key = song_keys[i]
        pychord_song_keys.append(Chord(song_key))

    for i in range(len(chord_progressions)):  # convert strings in the chord_progressions list to pychord objects
        chord_progression = chord_progressions[i]
        chord_progression = re.sub(r"/", "|", chord_progression)  # temp substitute / with |
        chords_list = chord_progression.split("|")  # list of chords in the progression, separated
        chords_list = list(filter(None, chords_list))  # remove empty strings from list
        pychord_chord_list = []

        for chord in chords_list:
            pychord_chord_list.append(Chord(chord))

        pychord_chord_progressions.append(pychord_chord_list)  # chord_progressions is a list of lists

    return pychord_song_keys, pychord_chord_progressions


def transposer(original_key, original_progression, target_key):
    transposed_by = int()  # how many semitones the key has been transposed to reach the target key
    while str(original_key.chord) != target_key:
        transposed_by += 1
        original_key.transpose(1)

    pychord_transposed_progression = []  # progressions transposed to the target key
    transposed_progression = []  # progressions transposed to the target key (strings)

    for original_chord in original_progression:  # transpose each chord in the progression by transposed_by
        original_chord.transpose(transposed_by)
        pychord_transposed_progression.append(original_chord)
        transposed_progression.append(str(original_chord.chord))

    return transposed_progression, pychord_transposed_progression


def get_transposed_progressions(song_keys, chord_progressions):

    pychord_song_keys, pychord_chord_progressions = create_pychord_objects(song_keys, chord_progressions)

    pychord_transposed_progressions = []  # progressions in C major and A minor, with pychord objects in lists
    transposed_progressions = []  # progressions in C major and A minor, as strings in lists

    for i in range(len(pychord_song_keys)):
        original_key = pychord_song_keys[i]
        original_progression = pychord_chord_progressions[i]

        if str(original_key.quality) == "":  # if key is major
            transposed_progression, pychord_transposed_progression = transposer(original_key, original_progression, "C")

            pychord_transposed_progressions.append(pychord_transposed_progression)
            transposed_progressions.append(transposed_progression)

        if str(original_key.quality) == "m":  # if key is minor
            transposed_progression, pychord_transposed_progression = transposer(original_key, original_progression, "Am")

            pychord_transposed_progressions.append(pychord_transposed_progression)
            transposed_progressions.append(transposed_progression)

    return transposed_progressions, pychord_transposed_progressions
