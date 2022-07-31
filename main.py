import os, random, re, time, mido
from tkinter import filedialog, messagebox
from transposer import get_transposed_progressions
from tonic import resolve_progressions, find_tonic
from midi import create_midi, play_midi, stop_midi
from pychord import Chord
from graph import Graph
from structure import structure_song
from shutil import copytree, rmtree


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

    text = text.replace(" ", "")  # turn whitespace into just spaces
    chord_progressions = text.split()  # split on spaces, create list
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
    # length = 16
    length = (random.choices((1, 2, 4), weights=[12, 8, 1]))[0] * 4  # length of chord progression: 4, 8, 16 bars

    lengths_of_chords = []  # how many beats in the bar the chord uses

    def count_beats():
        total_beats = int()
        for b in lengths_of_chords:
            total_beats += b
        return total_beats

    while count_beats() < length*4:
        r = random.choices((4, 2), weights=[3, 1])[0]

        if lengths_of_chords:
            if len(lengths_of_chords) >= 2:
                if count_beats() % 4:
                    if lengths_of_chords[-1] == 4:
                        r = 2

        lengths_of_chords.append(r)
        if count_beats() > length*4:
            lengths_of_chords.pop()

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

    for k in range(len(lengths_of_chords)):
        if len(composition) >= 1:
            while lengths_of_chords[k] == 2 and composition[-1] == chord.value:
                chord = g.get_next_word(chord)
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
            transpose_chord_by = random.randrange(0, 12)
            e.transpose(transpose_chord_by)
        if randomness_q > 90:
            q = d.root + random.choice(qualities)
            e = Chord(q)
        elif randomness_q > 80:
            q = d.root + random.choice(basic_qualities)
            e = Chord(q)
        e.transpose(transpose_by)
        transposed_chords.append(e)

    # print(section, lengths_of_chords)
    create_midi(transposed_chords, section, length, lengths_of_chords)

    composition.clear()
    for i in transposed_chords:
        composition.append(i.chord)

    string = ""
    beats_running_total = int()
    # is_long_progression = False
    # if length == 16:
    #     is_long_progression = True

    for j in range(len(composition)):
        if not string:
            string += composition[j]
            if lengths_of_chords[j] == 2:
                string += "//"
        else:
            if not beats_running_total % 4:  # if beat number divisible by four (start of bar)
                if lengths_of_chords[j] == 4:
                    string += " | " + composition[j]
                elif lengths_of_chords[j] == 2:
                    string += " | " + composition[j] + "//"
            else:  # if in middle of bar
                if lengths_of_chords[j] == 4:
                    string += " " + composition[j] + "// | " + composition[j] + "//"
                elif lengths_of_chords[j] == 2:
                    string += " " + composition[j] + "//"
            # if not beats_running_total % 4:  # if beat number divisible by four (start of bar)
            #     if lengths_of_chords[j] == 4:
            #         string += " | " + composition[j]
            #     if is_long_progression and beats_running_total == 28:
            #         string += " | \n           "
            #     if lengths_of_chords[j] == 2:
            #         string += " | " + composition[j] + "//"
            # else:  # if in middle of bar
            #     if is_long_progression and beats_running_total == 30:
            #         if lengths_of_chords[j] == 4:
            #             string += " " + composition[j] + "// | " + "\n            | " + composition[j] + "//"
            #         elif lengths_of_chords[j] == 2:
            #             string += " " + composition[j] + "// | "
            #     if is_long_progression and beats_running_total == 32:
            #         if lengths_of_chords[j] == 4:
            #             string += " " + composition[j] + "// | " + "\n            | " + composition[j] + "//"
            #         elif lengths_of_chords[j] == 2:
            #             string += " " + composition[j] + "// | " + "\n            | "
            #     else:
            #         if lengths_of_chords[j] == 4:
            #             string += " " + composition[j] + "// | " + composition[j] + "//"
            #         elif lengths_of_chords[j] == 2:
            #             string += " " + composition[j] + "//"

        beats_running_total += lengths_of_chords[j]

    return string


def main():
    transposed_progressions, pychord_transposed_progressions, song_sections, song_keys = get_chords_from_file("songs_chords.txt")

    transpose_by = random.randrange(0, 12)
    tonality = random.choice(("major", "minor"))

    # g = graph, s = possible starting chords, k = keys of starting chords
    intro_g, intro_s, intro_k = make_graph(transposed_progressions, song_sections, "intro", song_keys)
    intro = compose(intro_g, intro_s, intro_k, "intro", transpose_by, tonality)

    verse_g, verse_s, verse_k = make_graph(transposed_progressions, song_sections, "verse", song_keys)
    verse = compose(verse_g, verse_s, verse_k, "verse", transpose_by, tonality)

    prechorus_g, prechorus_s, prechorus_k = make_graph(transposed_progressions, song_sections, "prechorus", song_keys)
    prechorus = compose(prechorus_g, prechorus_s, prechorus_k, "prechorus", transpose_by, tonality)

    chorus_g, chorus_s, chorus_k = make_graph(transposed_progressions, song_sections, "chorus", song_keys)
    chorus = compose(chorus_g, chorus_s, chorus_k, "chorus", transpose_by, tonality)

    postchorus_g, postchorus_s, postchorus_k = make_graph(transposed_progressions, song_sections, "postchorus", song_keys)
    postchorus = compose(postchorus_g, postchorus_s, postchorus_k, "postchorus", transpose_by, tonality)

    bridge_g, bridge_s, bridge_k = make_graph(transposed_progressions, song_sections, "bridge", song_keys)
    bridge = compose(bridge_g, bridge_s, bridge_k, "bridge", transpose_by, tonality)

    interlude_g, interlude_s, interlude_k = make_graph(transposed_progressions, song_sections, "interlude", song_keys)
    interlude = compose(interlude_g, interlude_s, interlude_k, "interlude", transpose_by, tonality)

    outro_g, outro_s, outro_k = make_graph(transposed_progressions, song_sections, "outro", song_keys)
    outro = compose(outro_g, outro_s, outro_k, "outro", transpose_by, tonality)

    outro_g, other_s, other_k = make_graph(transposed_progressions, song_sections, "other", song_keys)
    other = compose(outro_g, other_s, other_k, "other", transpose_by, tonality)

    song_name = "SONG NAME"
    artist = "ARTIST"
    tonic = find_tonic(transpose_by, tonality)

    print(f"{song_name} by {artist} (Key: {tonic} {tonality})\n")
    s = structure_song()

    def get_prog_length(prog):  # get number of bars in chord progression
        return len(prog.split("|"))

    def get_multiplier(*args):
        l = get_prog_length(args[0])
        if len(args) == 1:  # if not intro, pre-chorus or post-chorus
            if l == 4:
                multiplier = (random.choices((1, 2, 4), weights=[1, 8, 6]))[0]  # how many times to loop the chord progression
            elif l == 8:
                multiplier = (random.choice((1, 2)))  # how many times to loop the chord progression
            else:
                multiplier = 1
        else:  # if intro, pre-chorus or post-chorus, these should be shorter than other sections
            if l == 4:
                multiplier = (random.choices((1, 2), weights=[1, 6]))[0]  # how many times to loop the chord progression
            else:
                multiplier = 1
        return multiplier

    def create_playlist():
        creating_playlist = []  # list of midi files to play to create song
        output = ""
        for i in s:
            match i:
                case "Intro":
                    m = get_multiplier(intro, "")
                    output += "Intro       : " + intro + " :  x" + str(m) + "\n"
                    for i in range(m):
                        creating_playlist.append("chord_midi/full/intro.mid")
                case "Verse":
                    m = get_multiplier(verse)
                    output += "Verse       : " + verse + " :  x" + str(m) + "\n"
                    for i in range(m):
                        creating_playlist.append("chord_midi/full/verse.mid")
                case "Pre-chorus":
                    m = get_multiplier(prechorus, "")
                    output += "Pre-chorus  : " + prechorus + " :  x" + str(m) + "\n"
                    for i in range(m):
                        creating_playlist.append("chord_midi/full/prechorus.mid")
                case "Chorus":
                    m = get_multiplier(chorus)
                    output += "Chorus      : " + chorus + " :  x" + str(m) + "\n"
                    for i in range(m):
                        creating_playlist.append("chord_midi/full/chorus.mid")
                case "Post-chorus":
                    m = get_multiplier(postchorus, "")
                    output += "Post-chorus : " + postchorus + " :  x" + str(m) + "\n"
                    for i in range(m):
                        creating_playlist.append("chord_midi/full/postchorus.mid")
                case "Bridge":
                    m = get_multiplier(bridge)
                    output += "Bridge      : " + bridge + " :  x" + str(m) + "\n"
                    for i in range(m):
                        creating_playlist.append("chord_midi/full/bridge.mid")
                case "Interlude":
                    m = get_multiplier(interlude)
                    output += "Interlude   : " + interlude + " :  x" + str(m) + "\n"
                    for i in range(m):
                        creating_playlist.append("chord_midi/full/interlude.mid")
                case "Outro":
                    m = get_multiplier(outro)
                    output += "Outro       : " + outro + " :  x" + str(m) + "\n"
                    for i in range(m):
                        creating_playlist.append("chord_midi/full/outro.mid")
                case "Other":
                    m = get_multiplier(other)
                    output += "Other       : " + other + " :  x" + str(m) + "\n"
                    for i in range(m):
                        creating_playlist.append("chord_midi/full/other.mid")

        print(output)
        with open("chord_midi/chords.txt", "w") as output_txt:
            output_txt.write(f"{song_name} by {artist} (Key: {tonic} {tonality})\n\n" + output)

        return creating_playlist

    total_seconds = float()

    playlist = create_playlist()
    for p in playlist:
        mid = mido.MidiFile(p)
        total_seconds += mid.length

    def convert(seconds):
        minutes, sec = divmod(seconds, 60)
        return "%02d:%02d" % (minutes, sec)

    print("Length " + convert(total_seconds))
    with open("chord_midi/chords.txt", "a") as output_txt:
        output_txt.write("\nLength " + convert(total_seconds))

    return playlist


if __name__ == '__main__':
    user_exit = False
    v = 0
    export_file_path = ""
    playlist = []

    def export_to():
        global export_file_path
        selected_folder = filedialog.askdirectory(title="Choose a folder to export MIDI files to")
        if selected_folder != "":
            export_file_path = selected_folder.replace("/", "\\")

            to_directory = os.path.join(export_file_path, "chord_midi")
            from_directory = "chord_midi"
            cancel = False
            if os.path.exists(to_directory):
                if messagebox.askokcancel(title="Exporting MIDI files", message="Folder 'chord_midi' already exists in this location. "
                                                                                "Overwrite?"):
                    rmtree(to_directory)
                else:
                    print("Exporting MIDIs cancelled.\n")
                    time.sleep(1)
                    cancel = True
            if not cancel:
                copytree(from_directory, to_directory)
                print("\nMIDIs exported to " + to_directory + "\n")
                time.sleep(1)
        else:
            print("Exporting MIDIs cancelled.\n")
            time.sleep(1)

    def cls():  # clear terminal
        print("\033[H\033[J", end="")

    while not user_exit:
        if v == 0:
            input("Press enter to generate a new progression.")
            cls()
            playlist = main()
            print("Press Ctrl + C stop playback.")
            try:
                for p in playlist:
                    play_midi(p)
            except KeyboardInterrupt:
                stop_midi()
                print("Playback stopped.\n")
                time.sleep(1)
            print("")
            v = 1

        print("Input R to replay, E to export MIDI files, or X to quit.")
        user_input = input("Input any other key to generate a new progression.\n")

        if user_input.lower() == "r":
            try:
                for p in playlist:
                    play_midi(p)
            except KeyboardInterrupt:
                stop_midi()
                print("Playback stopped.\n")
                time.sleep(1)

        elif user_input.lower() == "e":
            export_to()

        elif user_input.lower() == "x":
            user_exit = True

        else:
            confirm = input("Confirm create new? Input C to confirm, or any other letter to cancel.\n")
            if confirm.lower() == "c":
                cls()
                playlist = main()
                print("Press Ctrl + C stop playback.")
                try:
                    for p in playlist:
                        play_midi(p)
                except KeyboardInterrupt:
                    stop_midi()
                    print("Playback stopped.\n")
                    time.sleep(1)
