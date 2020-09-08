import json
from mido import MetaMessage, MidiTrack, Message
from glob import glob
from random import choice
from typing import List, Dict, Union, cast

# "Crash Cymbal 1" is Crash Cymbal 1
# "Ride Cymbal 1" is Ride Cymbal 1
# "Claves" is Claves

drum_types: dict = {
    "Acoustic Bass Drum": 0x23,
    "Bass Drum 1": 0x24,
    "Side Stick": 0x25,
    "Acoustic Snare": 0x26,
    "Closed Hi Hat": 0x2a,
    "Pedal Hi Hat": 0x2c,
    "Open Hi Hat": 0x2e,
    "Crash Cymbal 1": 0x31,
    "Ride Cymbal 1": 0x33,
    "Claves": 0x4b
}

file_list: List[str] = glob("data/drum_patterns/*.json")

# Format as json:
# {
#     "name": a unique name,
#     "pattern": [
#         {
#             "noteEvent": either "on" or "off",
#             "drumType": any drum type listed in drum_gen.drum_types,
#             "time": measured in 1/480 of a quarter note
#         },
#         {
#             "repeat_count": a number of times to repeat the subpattern,
#             "subpattern": {
#                 {
#                     "noteEvent": either "on" or "off",
#                     "drumType": any drum type listed in drum_gen.drum_types,
#                     "time": measured in 1/480 of a quarter note
#                 },
#                 {
#                     "repeat_count": a number of times to repeat the subpattern,
#                     "subpattern": {}
#                 }#             }
#         }
#     ]
# }
drumPatterns: List[Dict[str, Union[str, int, List[Dict[str, Union[str, int, Dict[str, Union[str, list]]]]]]]] = []


def get_drum_types() -> Dict[str, int]:
    """Gets a copy of the dictionary of drum types

    :return: The dictionary of drum types
    :rtype: Dict[str, int]
    """
    return drum_types.copy()


def read_patterns():
    """Reads the drum patterns in from a folder"""
    global drumPatterns
    drumPatterns = []
    for file_path in file_list:
        with open(file_path) as json_file:
            drumPatterns.append(json.load(json_file))


def get_patterns() -> List[Dict[str, Union[str, int, List[Dict[str, Union[str, int, Dict[str, Union[str, list]]]]]]]]:
    """Gets a copy of the list of drum patterns

    :return: The list of drum patterns
    :rtype: List[Dict[str, Union[str, int, List[Dict[str, Union[str, int, Dict[str, Union[str, list]]]]]]]]
    """
    return drumPatterns.copy()


def filter_patterns(chosen: List[int]):
    """Filters the drum patterns only to the ones chosen

    :param chosen: A list of numbers of the chosen drum patterns
    :type chosen: List[int]
    """
    global drumPatterns
    temp: List[Dict[str, Union[str, int, List[Dict[str, Union[str, int, Dict[str, Union[str, list]]]]]]]] = []
    for i in chosen:
        temp.append(drumPatterns[i])
    drumPatterns = temp


def drum_pattern_repeat_recursion(level: Dict[str, Union[str, Dict[str, Union[str, list]], int]], drum_track: MidiTrack):
    """Parses, recurisvely, a drum pattern and adds note_events

    :param level: The current level of the nested pattern
    :type level: Dict[str, Union[str, Dict[str, Union[str, list]], int]]
    :param drum_track: The drum track to add note events to
    :type drum_track: mido.MidiTrack
    """
    if "repeat_count" in level:
        for a in range(0, cast(int, level["repeat_count"])):
            for b in cast(List[Dict[str, Union[str, Dict[str, Union[str, list]], int]]], level["subpattern"]):
                drum_pattern_repeat_recursion(cast(Dict[str, Union[str, Dict[str, Union[str, list]], int]], b), drum_track)
    else:
        if (level["noteEvent"] == "on"):
            drum_track.append(Message('note_on', note=drum_types[level["drumType"]], channel=9, time=level["time"]))
        elif (level["noteEvent"] == "off"):
            drum_track.append(Message('note_off', note=drum_types[level["drumType"]], channel=9, time=level["time"]))
        else:
            print("whoops")


def drum(track: MidiTrack):
    """Picks a drum pattern and adds it to the track

    :param track: The drum track to add patterns to
    :type track: mido.MidiTrack
    """
    pattern: Dict[str, Union[str, int, List[Dict[str, Union[str, int, Dict[str, Union[str, list]]]]]]] = choice(drumPatterns)
    track.append(MetaMessage('text', text=cast(str, pattern['name'])))
    for i in cast(List[Dict[str, Union[str, Dict[str, Union[str, list]], int]]], pattern['pattern']):
        drum_pattern_repeat_recursion(i, track)


def create_drum_track(measures: int) -> MidiTrack:
    """Creates a drum track given a specific length

    :param measures: The total number of measures for the track
    :type meaures: int
    :return: The generated drum track
    :rtype: mido.MidiTrack
    """
    drum_track: MidiTrack = MidiTrack()
    drum_track.append(MetaMessage('instrument_name', name='Drum set'))
    for _ in range(0, measures):
        drum(drum_track)
    drum_track.append(MetaMessage('end_of_track'))
    return drum_track


def setup_patterns():
    """Initializes the entire set of drum patterns

    Todo: ask user for specific patterns
    """
    read_patterns()
    totalPatterns: int = len(get_patterns())
    a: List[int] = []
    for i in range(0, totalPatterns):
        a.append(i)
    filter_patterns(a)
