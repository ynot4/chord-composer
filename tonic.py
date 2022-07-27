def resolve_progressions(file_path, song_keys, chord_progressions):  # adds tonic chord to end of progression
    with open(file_path, encoding="utf-8-sig") as file:
        index = 0
        for line in file:
            if line[0] == "#" or line == "\n":
                continue
            else:
                chord_progressions[index] += f"|{song_keys[index]}"
                index += 1

    return chord_progressions


def find_tonic(transpose_by, tonality):
    if tonality == "minor":
        transpose_by_minor = transpose_by - 3
        if transpose_by_minor <= 0:
            transpose_by_minor += 12
        transpose_by = transpose_by_minor

    if transpose_by == 1:
        if tonality == "major":
            tonic = "Db"
        else:
            tonic = "C#"
    elif transpose_by == 2:
        tonic = "D"
    elif transpose_by == 3:
        if tonality == "major":
            tonic = "Eb"
        else:
            tonic = "D#"
    elif transpose_by == 4:
        tonic = "E"
    elif transpose_by == 5:
        tonic = "F"
    elif transpose_by == 6:
        if tonality == "major":
            tonic = "Gb"
        else:
            tonic = "F#"
    elif transpose_by == 7:
        tonic = "G"
    elif transpose_by == 8:
        if tonality == "major":
            tonic = "Ab"
        else:
            tonic = "G#"
    elif transpose_by == 9:
        tonic = "A"
    elif transpose_by == 10:
        tonic = "Bb"
    elif transpose_by == 11:
        tonic = "B"
    else:
        tonic = "C"
    return tonic
