import random, re
from transposer import get_transposed_progressions
from tonic import resolve_progressions, find_tonic
from midi import create_midi, play_midi
from pychord import Chord
from graph import Graph
from structure import structure_song


def get_chords_from_file(file_path):
    with open(file_path, encoding="utf-8-sig") as file:
        text = ""
        song_keys = []
        song_sections = []
        for line in file:
            if line[0] == "#" or line == "\n":
                continue
            else:
                square_brackets = re.search(r"^\[[^\]]*]", line)  # get all text inside the []
                # artist = re.search(r"^\[.*\—", square_brackets.group()).group()[1:-2]
                # # get match of '[text —' and ignore first character [ and space with em-dash
                # song = re.search(r"\B—.*\(", square_brackets.group()).group()[2:-2]
                # # get match of '— text (' and ignore unused characters
                sections = re.search(r"\B\(.*\)", square_brackets.group()).group()[1:-1]
                # get characters in bracket pair and ignore brackets
                sections_tuple = tuple(sections.split(","))
                song_sections.append(sections_tuple)

                song_key = re.split(r"{(.+)}", line)[1]  # get {key}
                song_keys.append(song_key)

                line_chords_only = re.sub(r"\[(.+)\]", "", line)  # remove [artist — song (song section)]
                line_chords_only = re.sub(r"{(.+)}", "", line_chords_only)  # remove {key}
                line_chords_only = re.sub(r":", "", line_chords_only)  # remove colon characters :
                text += line_chords_only

    text = ' '.join(text.split())  # turn whitespace into just spaces
    chord_progressions = text.split()  # split on spaces again, create list
    chord_progressions = resolve_progressions(file_path, song_keys, chord_progressions)

    transposed_progressions, pychord_transposed_progressions = get_transposed_progressions(song_keys, chord_progressions)

    return transposed_progressions, pychord_transposed_progressions, song_sections, song_keys


def separate_sections(section):
    match section:
        case "intro":
            tuple_values = ("I", "A", "AB", "AP")
        case "verse":
            tuple_values = ("V", "A", "AB", "AP")
        case "prechorus":
            tuple_values = ("P", "A", "AB")
        case "chorus":
            tuple_values = ("C", "A", "AB", "AP")
        case "postchorus":
            tuple_values = ("Po", "A", "AB", "AP")
        case "bridge":
            tuple_values = ("B", "A", "AP")
        case "interlude":
            tuple_values = ("D", "A", "AP", "AB")
        case "outro":
            tuple_values = ("O", "A", "AP", "AB")
        case other:
            tuple_values = ("E", "A", "AP", "AB")
    return tuple_values


def make_graph(transposed_progressions, song_sections, section, song_keys):
    g = Graph()
    prev_chord = None

    tuple_values = separate_sections(section)
    starting_chords = []
    starting_chords_keys = []  # key of progression with starting chord

    # for each progression
    for i in range(len(transposed_progressions)):

        use_progression = False  # only add progression to graph if right section

        for j in song_sections[i]:  # for each item in ("V","C") etc
            if j in tuple_values:  # if current item is in the tuple 'tuple_values' ("E", "A", "AP", "AB") etc
                use_progression = True
                break

        progression = transposed_progressions[i]  # for list (progression) in list (transposed_progressions)
        if use_progression:
            starting_chords.append(progression[0])
            starting_chords_keys.append(song_keys[i])
            for chord in progression:  # for each chord
                # check the chord is in the graph, and if not then add it
                chord_vertex = g.get_vertex(chord)
                # if there was a previous chord, then add an edge if it does not exist
                # if exists, increment weight by 1
                if prev_chord:  # prev chord should be a Vertex
                    # check if edge exists from the previous chord to current chord
                    prev_chord.increment_edge(chord_vertex)
                prev_chord = chord_vertex

    g.generate_probability_mappings()
    return g, starting_chords, starting_chords_keys


def compose(g, starting_chords, starting_chords_keys, section, transpose_by, tonality):
    length = (random.choices((1, 2, 4), weights=[12, 8, 1]))[0] * 4  # length of chord progression: 4, 8, 16 bars

    lengths_of_chords = []  # how many beats in the bar the chord uses

    def count_beats():
        total_beats = int()
        for b in lengths_of_chords:
            total_beats += b[0]
        return total_beats

    while count_beats() < length*4:
        r = random.choices((4, 2), weights=[5, 1])
        lengths_of_chords.append(r)
        if count_beats() > length*4:
            lengths_of_chords.pop()

    print(lengths_of_chords)

    starting_chords_tonality = []  # starting chords with correct tonality (major/minor)

    for i in range(len(starting_chords_keys)):  # get a list of starting chords for the chosen tonality
        c = starting_chords[i]
        k = starting_chords_keys[i]
        if tonality == "major":  # if major key
            if k[-1] != "m":
                starting_chords_tonality.append(c)
        else:  # if minor key
            if k[-1] == "m":
                starting_chords_tonality.append(c)

    composition = []
    s = random.choice(starting_chords_tonality)
    chord = g.get_vertex(s)

    for _ in range(length):
        composition.append(chord.value)
        chord = g.get_next_word(chord)

    basic_qualities = ['', 'm', 'dim', 'aug', 'sus2', 'sus4', '6', 'm6', '7', 'm7', 'maj7']
    qualities = ['', 'm', 'dim', 'aug', 'sus2', 'sus4', '6', '7', '7-5', '7b5', '7#5', '7sus4', 'm6', 'm7', 'm7-5', 'm7b5', 'm7#5',
                 'dim6', 'dim7', 'maj7', 'M7+5', 'mM7', 'add4', 'Madd4', 'madd4', 'add9', 'Madd9', 'madd9', 'sus4add9', 'sus4add2', '2',
                 'add11', '4', 'm69', '69', '9', 'm9', 'maj9', '9sus4', '7-9', '7b9', '7#9', '9-5', '9b5', '9#5', '7#9b5', '7#9#5',
                 'm7b9b5', '7b9b5', '7b9#5']

    chords = [Chord(c) for c in composition]
    transposed_chords = []

    for d in chords:
        randomness_r = random.randrange(0, 100)  # randomness for chord root
        randomness_q = random.randrange(0, 100)  # randomness for chord quality
        e = d
        if randomness_r > 90:
            up_or_down = random.randrange(-11, 12)
            e.transpose(up_or_down)
        if randomness_q > 90:
            q = d.root + random.choice(qualities)
            e = Chord(q)
        elif randomness_q > 80:
            q = d.root + random.choice(basic_qualities)
            e = Chord(q)
        e.transpose(transpose_by)
        transposed_chords.append(e)

    create_midi(transposed_chords, section)

    composition.clear()
    for i in transposed_chords:
        composition.append(i.chord)

    return composition


def main():
    transposed_progressions, pychord_transposed_progressions, song_sections, song_keys = get_chords_from_file("songs_chords.txt")

    # g = graph, s = possible starting chords, k = keys of starting chords
    intro_g, intro_s, intro_k = make_graph(transposed_progressions, song_sections, "intro", song_keys)
    verse_g, verse_s, verse_k = make_graph(transposed_progressions, song_sections, "verse", song_keys)
    prechorus_g, prechorus_s, prechorus_k = make_graph(transposed_progressions, song_sections, "prechorus", song_keys)
    chorus_g, chorus_s, chorus_k = make_graph(transposed_progressions, song_sections, "chorus", song_keys)
    postchorus_g, postchorus_s, postchorus_k = make_graph(transposed_progressions, song_sections, "postchorus", song_keys)
    bridge_g, bridge_s, bridge_k = make_graph(transposed_progressions, song_sections, "bridge", song_keys)
    interlude_g, interlude_s, interlude_k = make_graph(transposed_progressions, song_sections, "interlude", song_keys)
    outro_g, outro_s, outro_k = make_graph(transposed_progressions, song_sections, "outro", song_keys)

    transpose_by = random.randrange(0, 12)
    tonality = random.choice(("major", "minor"))

    intro = compose(intro_g, intro_s, intro_k, "intro", transpose_by, tonality)
    verse = compose(verse_g, verse_s, verse_k, "verse", transpose_by, tonality)
    prechorus = compose(prechorus_g, prechorus_s, prechorus_k, "prechorus", transpose_by, tonality)
    chorus = compose(chorus_g, chorus_s, chorus_k, "chorus", transpose_by, tonality)
    postchorus = compose(postchorus_g, postchorus_s, postchorus_k, "postchorus", transpose_by, tonality)
    bridge = compose(bridge_g, bridge_s, bridge_k, "bridge", transpose_by, tonality)
    interlude = compose(interlude_g, interlude_s, interlude_k, "interlude", transpose_by, tonality)
    outro = compose(outro_g, outro_s, outro_k, "outro", transpose_by, tonality)

    song_name = "SONG NAME"
    artist = "ARTIST"
    tonic = find_tonic(transpose_by, tonality)

    print(f"{song_name} by {artist} (Key: {tonic} {tonality})\n")
    s = structure_song()
    playlist = []  # list of midi files to play to create song

    for i in s:
        match i:
            case "Intro":
                print("Intro       :" + "|".join(intro) + ":")
                playlist.append("chord_midi/0 - intro.mid")
            case "Verse":
                print("Verse       :" + "|".join(verse) + ":")
                playlist.append("chord_midi/1 - verse.mid")
            case "Pre-chorus":
                print("Pre-chorus  :" + "|".join(prechorus) + ":")
                playlist.append("chord_midi/2 - prechorus.mid")
            case "Chorus":
                print("Chorus      :" + "|".join(chorus) + ":")
                playlist.append("chord_midi/3 - chorus.mid")
            case "Post-chorus":
                print("Post-chorus :" + "|".join(postchorus) + ":")
                playlist.append("chord_midi/4 - postchorus.mid")
            case "Bridge":
                print("Bridge      :" + "|".join(bridge) + ":")
                playlist.append("chord_midi/5 - bridge.mid")
            case "Interlude":
                print("Interlude   :" + "|".join(interlude) + ":")
                playlist.append("chord_midi/6 - interlude.mid")
            case "Outro":
                print("Outro       :" + "|".join(outro) + ":")
                playlist.append("chord_midi/7 - outro.mid")

    for p in playlist:
        play_midi(p)


if __name__ == '__main__':
    user_exit = False
    main()
    while not user_exit:
        user_input = input("Press R to replay or X to quit. Press any other key to generate a new progression.\n")
        if user_input.lower() == "r":
            play_midi("chord_midi/3 - chorus.mid")
        elif user_input.lower() == "x":
            user_exit = True
        else:
            main()
