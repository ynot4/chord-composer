import pretty_midi
import os

os.environ['PYGAME_HIDE_SUPPORT_PROMPT'] = "hide"
import pygame


def create_midi(chords, section, progression_length, chord_lengths):
    if progression_length == 4:
        midi_data = pretty_midi.PrettyMIDI("chord_midi/drums/4_bars.mid")
    elif progression_length == 8:
        midi_data = pretty_midi.PrettyMIDI("chord_midi/drums/8_bars.mid")
    else:
        midi_data = pretty_midi.PrettyMIDI("chord_midi/drums/16_bars.mid")

    piano_only = pretty_midi.PrettyMIDI()

    piano_program = pretty_midi.instrument_name_to_program("Electric Piano 1")
    piano = pretty_midi.Instrument(program=piano_program)

    bass_program = pretty_midi.instrument_name_to_program("Fretless Bass")
    bass = pretty_midi.Instrument(program=bass_program)

    length = 2

    chord_index = 0
    index = 0
    for chord in chords:  # piano chords to midi
        for note_name in chord.components_with_pitch(root_pitch=4):
            note_number = pretty_midi.note_name_to_number(note_name)
            if chord_lengths[index] == 4:
                note = pretty_midi.Note(velocity=100, pitch=note_number, start=chord_index, end=(chord_index + length))
            elif chord_lengths[index] == 2:
                note = pretty_midi.Note(velocity=100, pitch=note_number, start=chord_index, end=(chord_index + length/2))
            else:
                raise ValueError("Length of chord is not 2 or 4 beats.")
            piano.notes.append(note)

        if chord_lengths[index] == 4:
            chord_index += length
        elif chord_lengths[index] == 2:
            chord_index += length/2
        index += 1

    chord_index = 0
    index = 0
    for chord in chords:  # create bouncy bass-line
        if chord_lengths[index] == 4:
            r = 8
        elif chord_lengths[index] == 2:
            r = 4
        else:
            raise ValueError("Length of chord is not 2 or 4 beats.")

        l = length/8
        for i in range(r):
            if i % 2:  # skip odd values of i
                continue
            note_number = pretty_midi.note_name_to_number(chord.root + "1")
            note = pretty_midi.Note(velocity=100, pitch=note_number, start=i * l + chord_index, end=(i + 1) * l + chord_index)
            bass.notes.append(note)
            i += 1
            note_number = pretty_midi.note_name_to_number(chord.root + "2")
            note = pretty_midi.Note(velocity=90, pitch=note_number, start=i * l + chord_index, end=(i + 1) * l + chord_index)
            bass.notes.append(note)

        if chord_lengths[index] == 4:
            chord_index += length
        elif chord_lengths[index] == 2:
            chord_index += length/2
        index += 1

    midi_data.instruments.append(piano)
    midi_data.instruments.append(bass)
    piano_only.instruments.append(piano)

    file_name = f"chord_midi/full/{section}.mid"
    piano_file_name = f"chord_midi/piano/{section}.mid"
    midi_data.write(file_name)
    piano_only.write(piano_file_name)


def play_midi(midi_filename):
    """Stream music_file in a blocking manner"""

    # mixer config
    freq = 44100  # audio CD quality
    bitsize = -16  # unsigned 16 bit
    channels = 2  # 1 is mono, 2 is stereo
    buffer = 512  # number of samples
    pygame.mixer.pre_init(freq, bitsize, channels, buffer)
    pygame.mixer.init()
    pygame.init()

    # optional volume 0 to 1.0
    pygame.mixer.music.set_volume(0.8)
    clock = pygame.time.Clock()
    pygame.mixer.music.load(midi_filename)
    pygame.mixer.music.play()

    while pygame.mixer.music.get_busy():
        clock.tick(30)  # check if playback has finished


def stop_midi():
    pygame.mixer.music.stop()
