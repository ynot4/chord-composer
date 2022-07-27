"""
Created on 3/7/17, 9:28 AM

@author: davecohen

Title: Random Chord Progression Generator
    Major, Minor, Diminished, Augmented
"""
import random


def chords(ch_num):
    '''Generates a random chord progression (printed both as sharps and flats) as a string given an integer number of chords as an argument.
    '''
    ch_root = ['C', 'C#', 'D', 'D#', 'E', 'F', 'F#', 'G', 'G#', 'A', 'A#', 'B', ]
    ch_quality = ['', 'm', 'dim', '+']
    ch_prog = ''
    # generate string of 'num' chords
    for x in range(ch_num):
        rand_root = random.choice(ch_root)
        rand_quality = random.choice(ch_quality)
        ch_prog += str(rand_root + rand_quality + ' | ')
    print('Sharp (#) Version:')
    print('\t' + ch_prog)
    # convert string to flats
    ch_prog = ch_prog.replace('C#', 'Db')
    ch_prog = ch_prog.replace('D#', 'Eb')
    ch_prog = ch_prog.replace('F#', 'Gb')
    ch_prog = ch_prog.replace('G#', 'Ab')
    ch_prog = ch_prog.replace('A#', 'Bb')
    print('Flat (b) Version:')
    print('\t' + ch_prog)


# start
print('Generate Random Chord Progressions')

# user enters number of chords and print x number of progressions:
try:
    user_num = int(input('How many chords? (rec. 3-10) '))
    user_x = int(input('How many random progressions? (50 max) '))
    if user_num > 16: user_num = 16
    if user_num < 1: user_num = 3
    if user_x > 50: user_x = 50
    if user_x < 1: user_x = 3
# if user doesn't enter ints, a default is executed.
except:
    print('Number not entered. Generating default 10/10...')
    user_num = 10
    user_x = 10
# main function
for x in range(1, user_x + 1):
    print('{}/{}: Random Chord Progression of {} chords'.format(x, user_x, user_num))
    chords(user_num)
'''
How to save output as text?
'''
