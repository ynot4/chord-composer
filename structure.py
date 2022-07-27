import random


def structure_song():  # randomise song structure
    structure = []

    has_intro = bool(random.getrandbits(1))  # random boolean
    if has_intro:
        structure.append("Intro")
    start_with = random.choices(("Chorus", "Post-chorus", "Verse"), weights=[3, 1, 6])[0]
    if start_with != "Verse":
        structure.append(start_with)
    structure.append("Verse")
    if start_with == "Chorus":  # if song starts with chorus increase chance of pre-chorus
        has_prechorus = random.random() * 100 < 95  # return True if random number is smaller than 95
    else:
        has_prechorus = random.random() * 100 < 85  # return True if random number is smaller than 75
    if has_prechorus:
        structure.append("Pre-chorus")
    structure.append("Chorus")
    has_postchorus = random.random() * 100 < 60  # return True if random number is smaller than 60
    if has_postchorus or start_with == "Post-chorus":
        structure.append("Post-chorus")

    structure.append("Verse")
    if has_prechorus:
        structure.append("Pre-chorus")
    structure.append("Chorus")
    has_postchorus = random.random() * 100 < 30  # return True if random number is smaller than 60
    if has_postchorus:
        structure.append("Post-chorus")

    bridge_or = random.choices(("Bridge", "Interlude", "Verse"), weights=[5, 5, 1])[0]
    if bridge_or == "Bridge":
        structure.append(bridge_or)
        has_interlude = random.random() * 100 < 75  # return True if random number is smaller than 75
        if has_interlude:
            structure.append("Interlude")
    elif bridge_or == "Interlude":
        structure.append(bridge_or)
        has_bridge = random.random() * 100 < 75  # return True if random number is smaller than 75
        if has_bridge:
            structure.append("Bridge")
    else:
        structure.append("Verse")

    structure.append("Chorus")
    has_postchorus = random.random() * 100 < 80  # return True if random number is smaller than 60
    if has_postchorus:
        structure.append("Post-chorus")
    has_outro = bool(random.getrandbits(1))  # random boolean
    if has_outro:
        structure.append("Outro")

    return structure
