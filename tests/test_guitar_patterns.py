import glob
from src.guitar_gen import read_patterns, filter_patterns, create_track, get_patterns
from tests.test_main import type_sequences
from mido import MidiFile
from filecmp import cmp
from src.main import simple_pick_chords, simple_chord_order, create_simple_meta_track
from os import mkdir
from typing import List, Dict, Union, cast


def test_guitar():
    file_list: List[str] = glob.glob("data/guitar_patterns/*.json")
    for i in range(0, len(file_list)):
        progression_length: int = 4
        mid: MidiFile = MidiFile()
        mid.tracks.append(create_simple_meta_track()[0])
        read_patterns()
        filter_patterns([i])
        sequences: Dict[str, Union[List[List[List[int]]], List[str]]] = simple_chord_order(simple_pick_chords(progression_length))
        pattern = get_patterns()[0]
        guitar_patterns_types(pattern)
        type_sequences(sequences)
        mid.tracks.append(create_track(progression_length, sequences['values'], 1))
        try:
            mkdir("tests/output")
            print("Created tests/output directory.")
        except FileExistsError:
            pass
        try:
            mkdir("tests/output/guitar")
            print("Created tests/output/guitar directory.")
        except FileExistsError:
            pass
        file_name: str = pattern['name'] + '.mid'
        mid.save('tests/output/guitar/' + file_name)
        print(pattern['name'])
        assert abs(mid.length - 8) < .001
        assert cmp('tests/output/guitar/' + file_name, 'tests/data/guitar/' + file_name, shallow=False)


def recursive_parse_patterns(pattern: Dict[str, Union[str, Dict[str, Union[str, list]], int]]):
    if "repeat_count" in pattern:
        assert isinstance(pattern['repeat_count'], int)
        assert pattern['repeat_count'] > 1
        assert isinstance(pattern['subpattern'], list)
        assert len(pattern['subpattern']) > 1
        for a in range(0, cast(int, pattern["repeat_count"])):
            for b in cast(List[Dict[str, Union[str, Dict[str, Union[str, list]], int]]], pattern["subpattern"]):
                recursive_parse_patterns(cast(Dict[str, Union[str, Dict[str, Union[str, list]], int]], b))
    else:
        assert isinstance(pattern['note_event'], str)
        assert pattern['note_event'] == 'note_on' or pattern['note_event'] == 'note_off'
        assert isinstance(pattern['pitchIndex'], int)
        assert pattern['pitchIndex'] >= 0 and pattern['pitchIndex'] <= 3
        assert isinstance(pattern['time'], int)
        assert pattern['time'] >= 0


def guitar_patterns_types(pattern: Dict[str, Union[str, List[Dict[str, Union[str, int, Dict[str, Union[str, list]]]]]]]):
    assert isinstance(pattern, dict)
    assert 'name' in pattern
    assert isinstance(pattern['name'], str)
    assert len(pattern['name']) > 0
    assert 'ticksPerMeasure' in pattern
    assert isinstance(pattern['ticksPerMeasure'], int)
    assert pattern['ticksPerMeasure'] > 0
    assert 'measures' in pattern
    assert isinstance(pattern['measures'], int)
    assert pattern['measures'] > 0
    assert 'pattern' in pattern
    assert isinstance(pattern['pattern'], list)
    assert len(pattern['pattern']) > 0
    for event in pattern['pattern']:
        assert isinstance(event, dict)
        recursive_parse_patterns(event)
