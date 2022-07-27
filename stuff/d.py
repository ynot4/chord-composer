from tkinter import *
from tkinter import simpledialog
from midiutil import MIDIFile


def save_music(filename):
    with open(filename, "wb") as output:
        mid.writeFile(output)


def get_chord_notes(chord):
    if chord == 'A':
        chord = [A, C_SHARP, E]
    elif chord == 'Am':
        chord = [A, C, E]
    elif chord == 'A#' or chord == 'Bb':
        chord = [A_SHARP, D, F]
    elif chord == 'A#m' or chord == 'Bbm':
        chord = [A_SHARP, C_SHARP, F]
    elif chord == 'B':
        chord = [B, D_SHARP, F_SHARP]
    elif chord == 'Bm':
        chord = [B, D, F_SHARP]
    elif chord == 'C':
        chord = [C, E, G]
    elif chord == 'Cm':
        chord = [C, D_SHARP, G]
    elif chord == 'C#' or chord == 'Db':
        chord = [C_SHARP, F, G_SHARP]
    elif chord == 'C#m' or chord == 'Dbm':
        chord = [C_SHARP, E, G_SHARP]
    elif chord == 'D':
        chord = [D, F_SHARP, A]
    elif chord == 'Dm':
        chord = [D, F, A]
    elif chord == 'D#' or chord == 'Eb':
        chord = [D_SHARP, G, A_SHARP]
    elif chord == 'D#m' or chord == 'Ebm':
        chord = [D_SHARP, F_SHARP, A_SHARP]
    elif chord == 'E':
        chord = [E, G_SHARP, B]
    elif chord == 'Em':
        chord = [E, G, B]
    elif chord == 'F':
        chord = [F, A, C]
    elif chord == 'Fm':
        chord = [F, G_SHARP, C]
    elif chord == 'F#' or chord == 'Gb':
        chord = [F_SHARP, A_SHARP, C_SHARP]
    elif chord == 'F#m' or chord == 'Gbm':
        chord = [F_SHARP, A, C_SHARP]
    elif chord == 'G':
        chord = [G, B, D]
    elif chord == 'Gm':
        chord = [G, A_SHARP, D]
    elif chord == 'G#' or chord == 'Ab':
        chord = [G_SHARP, C, D_SHARP]
    elif chord == 'G#m' or chord == 'Abm':
        chord = [G_SHARP, B, D_SHARP]
    return chord


def get_first_chord(chord, octaves, real_notes):
    middle_note = round(sum(real_notes) / (12 * len(octaves)))
    chord = get_chord_notes(chord)
    real_chord = sorted([note for note in real_notes for chord_note in chord if note % 12 == chord_note])
    minimum_difference = [abs(note - middle_note) for note in real_chord]
    chord_middle = real_chord[minimum_difference.index(min(minimum_difference))]
    final_chord = [real_chord[real_chord.index(chord_middle) - 1], chord_middle,
                   real_chord[real_chord.index(chord_middle) + 1]]
    return final_chord


def get_chord_inversions(chords):
    octaves = [4, 5]
    real_notes = [12 * octave + note for octave in octaves for note in notes]
    chord_list = [get_first_chord(chords[0], octaves, real_notes)]
    other_chords = chords[1:]
    other_chords_notes = [get_chord_notes(chord) for chord in other_chords]
    for chord in range(len(other_chords)):
        reference_chord = chord_list[-1]
        real_chord = sorted(
            [note for note in real_notes for chord_note in other_chords_notes[chord] if note % 12 == chord_note])
        chord_combinations = [[real_chord[note], real_chord[note + 1], real_chord[note + 2]] for note in
                              range(len(real_chord) - 2)]
        differences = [
            [abs(reference_chord[note] - chord_combinations[combination][note]) for note in range(len(reference_chord))]
            for combination in range(len(chord_combinations))]
        minimum_sum = [sum(difference) for difference in differences]
        nearest_chord = chord_combinations[minimum_sum.index(min(minimum_sum))]
        chord_list.append(nearest_chord)
    return chord_list


def bassify(chord):
    octaves = [3]
    bass = [12 * octave + note for octave in octaves for note in notes]
    start = bass[0]
    if chord.startswith('A'):
        start = bass[0]
    elif chord.startswith('A#') or chord.startswith('Bb'):
        start = bass[1]
    elif chord.startswith('B'):
        start = bass[2]
    elif chord.startswith('C'):
        start = bass[3]
    elif chord.startswith('C#') or chord.startswith('Db'):
        start = bass[4]
    elif chord.startswith('D'):
        start = bass[5]
    elif chord.startswith('D#') or chord.startswith('Eb'):
        start = bass[6]
    elif chord.startswith('E'):
        start = bass[7]
    elif chord.startswith('F'):
        start = bass[8]
    elif chord.startswith('F#') or chord.startswith('Gb'):
        start = bass[9]
    elif chord.startswith('G'):
        start = bass[10]
    elif chord.startswith('G#') or chord.startswith('Ab'):
        start = bass[11]
    return start


def jumpy_guitar(chord_progressions, chord_basses, iterations, time, track, channel, chord_volume):
    jumpy_basses = []
    jumpy_chords = []
    for chord in range(len(chord_basses)):
        if chord % 2 == 0:
            jumpy_basses.append(chord_basses[chord])
            for i in range(2):
                jumpy_chords.append(chord_progressions[chord])
        else:
            for i in range(3):
                jumpy_basses.append(chord_basses[chord])
                jumpy_chords.append(chord_progressions[chord])
    jumpy_chords_duration = [duration for i in range(int(len(jumpy_chords) / 5)) for duration in
                             [1, 0.75, 0.5, 0.75, 1]]
    jumpy_basses_duration = [duration for i in range(int(len(jumpy_basses) / 8)) for duration in
                             [1.5, 1, 1, 0.5, 1.5, 1, 0.75, 0.75]]
    for i in range(iterations):
        for chord in range(len(jumpy_chords)):
            for note in range(len(jumpy_chords[chord])):
                mid.addNote(track, channel, jumpy_chords[chord][note], time, jumpy_chords_duration[chord], chord_volume)
            time += jumpy_chords_duration[chord]
    time = 0
    for i in range(iterations):
        for bass in range(len(jumpy_basses)):
            mid.addNote(track, channel, jumpy_basses[bass], time, jumpy_basses_duration[bass], chord_volume)
            time += jumpy_basses_duration[bass]


def enter_filename():
    filename = simpledialog.askstring(title='Input Filename',
                                      prompt='Enter desired filename (without file extension):') + '.mid'
    save_music(filename)


window = Tk()
window.title("Jumpy Chord Progression Generator \u2022 RVM Productions")
window.geometry('683x384')

menubar = Menu(window)
filemenu = Menu(menubar, tearoff=0)
filemenu.add_command(label='Save as MIDI...', command=enter_filename)
menubar.add_cascade(label='File', menu=filemenu)
window.config(menu=menubar)

A = 9
A_SHARP = 10
B = 11
C = 0
C_SHARP = 1
D = 2
D_SHARP = 3
E = 4
F = 5
F_SHARP = 6
G = 7
G_SHARP = 8
notes = [A, A_SHARP, B, C, C_SHARP, D, D_SHARP, E, F, F_SHARP, G, G_SHARP]

chord_volume = 127
track = 0
channel = 0
time = 0
mid = MIDIFile(1)

chord_inputs = simpledialog.askstring(title='Input Chord Progression',
                                      prompt='Enter chord progression separated by space (multiples of 4):')
chord_inputs = chord_inputs.split()
chord_progressions = get_chord_inversions(chord_inputs)
chord_basses = [bassify(chord) for chord in chord_inputs]
iterations = simpledialog.askinteger(title='Loop Chord Progression', prompt='Enter number of iterations:')

jumpy_guitar(chord_progressions, chord_basses, iterations, time, track, channel, chord_volume)

chords_label = Label(window, text='Recognized Chords: ')
chords_inputs_label = Label(window, text=chord_inputs)
iterations_label = Label(window, text='Number of Loops: ')
iterations_input_label = Label(window, text=str(iterations))
chords_label.place(relx=0.25, rely=0.25)
chords_inputs_label.place(relx=0.5, rely=0.25)
iterations_label.place(relx=0.25, rely=0.5)
iterations_input_label.place(relx=0.5, rely=0.5)

window.mainloop()