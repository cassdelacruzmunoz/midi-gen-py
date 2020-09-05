import glob
from src.drum_gen import readDrumPatterns, filterDrumPatterns, drum, getDrumPatterns
from mido import MidiTrack, MetaMessage, MidiFile
from filecmp import cmp
from os import mkdir


def test_drums():
    file_list = glob.glob("data/drum_patterns/*.json")
    for i in range(0, len(file_list)):
        mid = MidiFile()
        readDrumPatterns()
        filterDrumPatterns([i])
        drumTrack = MidiTrack()
        drum(drumTrack)
        drumTrack.append(MetaMessage('end_of_track'))
        mid.tracks.append(drumTrack)
        try:
            mkdir("tests/output")
            print("Created output directory.")
        except FileExistsError:
            print()
        try:
            mkdir("tests/output/guitar")
            print("Created output directory.")
        except FileExistsError:
            print()
        mid.save('tests/output/drums/' + getDrumPatterns()[0]['name'] + '.mid')
        assert cmp('tests/output/drums/' + getDrumPatterns()[0]['name'] + '.mid', 'tests/data/drums/' + getDrumPatterns()[0]['name'] + '.mid', shallow=False)
