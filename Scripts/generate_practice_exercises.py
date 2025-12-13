#!/usr/bin/env python3
"""
generate_practice_exercises.py

Generates 34 MusicXML practice-exercise files (17 per tune) for:
- Tune02_Orbit (Wayne Shorter-style, 3/4, F major, 160 BPM)
- Tune11_Crystal_Silence (ECM ballad, 4/4, A major, 80 BPM)

Uses xml.etree.ElementTree to build MusicXML Partwise documents.
Creates directories if missing, verifies bar durations, prints progress.

Author: ChatGPT
"""

from __future__ import annotations

import os
import math
from dataclasses import dataclass
from typing import List, Optional, Tuple, Dict
import xml.etree.ElementTree as ET


# -----------------------------
# Music primitives
# -----------------------------

STEP_TO_SEMITONE = {"C": 0, "D": 2, "E": 4, "F": 5, "G": 7, "A": 9, "B": 11}
SEMITONE_TO_STEP_ALTER = {
    0: ("C", 0),
    1: ("C", 1),
    2: ("D", 0),
    3: ("E", -1),
    4: ("E", 0),
    5: ("F", 0),
    6: ("F", 1),
    7: ("G", 0),
    8: ("A", -1),
    9: ("A", 0),
    10: ("B", -1),
    11: ("B", 0),
}

OPEN_STRINGS_MIDI = {
    "E2": 40,
    "A2": 45,
    "D3": 50,
    "G3": 55,
    "B3": 59,
    "E4": 64,
}

def midi_to_pitch(midi: int) -> Tuple[str, int, int]:
    """Convert MIDI note number to (step, alter, octave). Uses sharps/flats mapping above."""
    octave = (midi // 12) - 1
    pc = midi % 12
    step, alter = SEMITONE_TO_STEP_ALTER[pc]
    return step, alter, octave

def pitch_to_midi(step: str, alter: int, octave: int) -> int:
    """Convert (step, alter, octave) to MIDI note number."""
    return (octave + 1) * 12 + STEP_TO_SEMITONE[step] + alter

def pc_from_step_alter(step: str, alter: int) -> int:
    return (STEP_TO_SEMITONE[step] + alter) % 12

def name_to_pc(name: str) -> int:
    """
    Parse pitch class name like: F, Bb, C#, Eb, etc.
    Returns pitch class 0..11.
    """
    name = name.strip()
    if not name:
        raise ValueError("Empty pitch name")
    step = name[0].upper()
    alter = 0
    if len(name) > 1:
        acc = name[1:]
        if acc == "b":
            alter = -1
        elif acc == "#":
            alter = 1
        elif acc == "bb":
            alter = -2
        elif acc == "##":
            alter = 2
        else:
            # allow "♭" or "♯"
            acc = acc.replace("♭", "b").replace("♯", "#")
            if acc == "b":
                alter = -1
            elif acc == "#":
                alter = 1
            else:
                raise ValueError(f"Unrecognized accidental in {name}")
    return (STEP_TO_SEMITONE[step] + alter) % 12

def nearest_midi_in_range(target_pc: int, prev_midi: int, lo: int, hi: int) -> int:
    """
    Choose a MIDI note within [lo, hi] whose pitch class == target_pc and
    is nearest to prev_midi (for smoothness).
    """
    candidates = []
    for midi in range(lo, hi + 1):
        if midi % 12 == target_pc:
            candidates.append(midi)
    if not candidates:
        # fallback: clamp prev_midi
        return max(lo, min(hi, prev_midi))
    return min(candidates, key=lambda m: (abs(m - prev_midi), m))

def choose_open_string_friendly(midi_options: List[int], prev_midi: int) -> int:
    """
    For ECM/campanella-ish writing: prefer pitches close to open strings
    (and also not too close to previous note to encourage ring).
    """
    open_midi = list(OPEN_STRINGS_MIDI.values())
    def score(m: int) -> float:
        dist_to_open = min(abs(m - o) for o in open_midi)
        step_size = abs(m - prev_midi)
        # prefer moderate leaps (campanella feel) and closeness to open strings
        return dist_to_open * 1.25 - min(step_size, 12) * 0.15
    return min(midi_options, key=score)

@dataclass
class TimeSig:
    beats: int
    beat_type: int

@dataclass
class TuneSpec:
    name: str
    short: str
    base_dir: str
    key_fifths: int
    tempo_qpm: int
    time: TimeSig
    divisions_per_quarter: int = 16

    @property
    def divisions_per_measure(self) -> int:
        # quarter-note divisions = 16
        # beats are in beat_type, convert to quarters
        # e.g. 3/4 => 3 quarters; 4/4 => 4 quarters
        quarter_factor = 4 / self.time.beat_type
        return int(self.time.beats * quarter_factor * self.divisions_per_quarter)

# -----------------------------
# MusicXML builders
# -----------------------------

def xml_note(step: str, alter: int, octave: int, duration: int,
             voice: int = 1, note_type: Optional[str] = None,
             tie_start: bool = False, tie_stop: bool = False) -> ET.Element:
    n = ET.Element("note")
    pitch = ET.SubElement(n, "pitch")
    ET.SubElement(pitch, "step").text = step
    if alter != 0:
        ET.SubElement(pitch, "alter").text = str(alter)
    ET.SubElement(pitch, "octave").text = str(octave)

    ET.SubElement(n, "duration").text = str(duration)
    ET.SubElement(n, "voice").text = str(voice)

    if tie_start:
        ET.SubElement(n, "tie", {"type": "start"})
    if tie_stop:
        ET.SubElement(n, "tie", {"type": "stop"})

    if note_type:
        ET.SubElement(n, "type").text = note_type
    return n

def xml_rest(duration: int, voice: int = 1, note_type: Optional[str] = None) -> ET.Element:
    n = ET.Element("note")
    ET.SubElement(n, "rest")
    ET.SubElement(n, "duration").text = str(duration)
    ET.SubElement(n, "voice").text = str(voice)
    if note_type:
        ET.SubElement(n, "type").text = note_type
    return n

def xml_backup(duration: int) -> ET.Element:
    b = ET.Element("backup")
    ET.SubElement(b, "duration").text = str(duration)
    return b

def note_type_from_duration(divisions_per_quarter: int, dur: int) -> str:
    """
    Map simple durations to MusicXML type.
    We only use common values: 16th, eighth, quarter, half, whole.
    """
    q = divisions_per_quarter
    if dur == q // 4:
        return "16th"
    if dur == q // 2:
        return "eighth"
    if dur == q:
        return "quarter"
    if dur == 2 * q:
        return "half"
    if dur == 4 * q:
        return "whole"
    # fallback
    return "quarter"

def create_score_root(title: str, tune: TuneSpec) -> ET.Element:
    score = ET.Element("score-partwise", {"version": "3.1"})
    work = ET.SubElement(score, "work")
    ET.SubElement(work, "work-title").text = title

    ident = ET.SubElement(score, "identification")
    enc = ET.SubElement(ident, "encoding")
    ET.SubElement(enc, "software").text = "generate_practice_exercises.py"

    part_list = ET.SubElement(score, "part-list")
    score_part = ET.SubElement(part_list, "score-part", {"id": "P1"})
    ET.SubElement(score_part, "part-name").text = "Guitar"

    part = ET.SubElement(score, "part", {"id": "P1"})
    return score

def add_attributes_and_tempo(measure: ET.Element, tune: TuneSpec) -> None:
    attrs = ET.SubElement(measure, "attributes")
    ET.SubElement(attrs, "divisions").text = str(tune.divisions_per_quarter)
    key = ET.SubElement(attrs, "key")
    ET.SubElement(key, "fifths").text = str(tune.key_fifths)
    time = ET.SubElement(attrs, "time")
    ET.SubElement(time, "beats").text = str(tune.time.beats)
    ET.SubElement(time, "beat-type").text = str(tune.time.beat_type)
    clef = ET.SubElement(attrs, "clef")
    ET.SubElement(clef, "sign").text = "G"
    ET.SubElement(clef, "line").text = "2"

    direction = ET.SubElement(measure, "direction", {"placement": "above"})
    d_type = ET.SubElement(direction, "direction-type")
    metro = ET.SubElement(d_type, "metronome")
    ET.SubElement(metro, "beat-unit").text = "quarter"
    ET.SubElement(metro, "per-minute").text = str(tune.tempo_qpm)

def write_musicxml(path: str, title: str, tune: TuneSpec, measures: List[ET.Element]) -> None:
    score = create_score_root(title, tune)
    part = score.find("./part[@id='P1']")
    assert part is not None

    for i, m in enumerate(measures, start=1):
        m.set("number", str(i))
        part.append(m)

    tree = ET.ElementTree(score)
    os.makedirs(os.path.dirname(path), exist_ok=True)
    tree.write(path, encoding="UTF-8", xml_declaration=True)

# -----------------------------
# Harmonic / scale material (internal selection)
# -----------------------------

def lydian_pc_set(root_name: str) -> List[int]:
    # Lydian: 1 2 3 #4 5 6 7
    root = name_to_pc(root_name)
    intervals = [0, 2, 4, 6, 7, 9, 11]
    return [(root + i) % 12 for i in intervals]

def lydian_aug_pc_set(root_name: str) -> List[int]:
    # Lydian Augmented: 1 2 3 #4 #5 6 7
    root = name_to_pc(root_name)
    intervals = [0, 2, 4, 6, 8, 9, 11]
    return [(root + i) % 12 for i in intervals]

def dorian_pc_set(root_name: str) -> List[int]:
    # Dorian: 1 2 b3 4 5 6 b7
    root = name_to_pc(root_name)
    intervals = [0, 2, 3, 5, 7, 9, 10]
    return [(root + i) % 12 for i in intervals]

def triad_pc_set(root_name: str, quality: str) -> List[int]:
    root = name_to_pc(root_name)
    if quality == "maj":
        ints = [0, 4, 7]
    elif quality == "min":
        ints = [0, 3, 7]
    elif quality == "aug":
        ints = [0, 4, 8]
    else:
        raise ValueError("quality must be maj/min/aug")
    return [(root + i) % 12 for i in ints]

# -----------------------------
# Generation utilities
# -----------------------------

def verify_measure_duration(measure: ET.Element, expected: int) -> int:
    """
    Sum durations for voice 1 only unless measure contains backup (two voices).
    We'll verify both voices if backups exist.
    """
    # Collect notes/rests by voice in encounter order, respecting backups.
    # Simplify: compute voice totals separately ignoring backups, because we
    # explicitly manage voice duration per measure in our own builders.
    voice_sums: Dict[str, int] = {}
    for n in measure.findall("./note"):
        voice = n.findtext("voice", default="1")
        dur = int(n.findtext("duration", default="0"))
        voice_sums[voice] = voice_sums.get(voice, 0) + dur

    # If two voices, expect each voice to sum expected (common on single staff with backup)
    if len(voice_sums) > 1:
        for v, s in voice_sums.items():
            if s != expected:
                raise ValueError(f"Measure duration mismatch (voice {v}): got {s}, expected {expected}")
    else:
        s = voice_sums.get("1", 0)
        if s != expected:
            raise ValueError(f"Measure duration mismatch: got {s}, expected {expected}")
    return expected

def make_eighth_arpeggio_bar(tune: TuneSpec, pc_pool: List[int], start_midi: int,
                            lo: int, hi: int, prefer_open: bool = False) -> Tuple[ET.Element, int]:
    """
    Fill one measure with continuous eighth notes.
    Orbit 3/4 => 6 eighths; Crystal 4/4 => 8 eighths.
    """
    m = ET.Element("measure")
    total = tune.divisions_per_measure
    dur_eighth = tune.divisions_per_quarter // 2
    count = total // dur_eighth

    prev = start_midi
    for i in range(count):
        pc = pc_pool[i % len(pc_pool)]
        # build candidate midis for this pitch class
        candidates = [mi for mi in range(lo, hi + 1) if mi % 12 == pc]
        if not candidates:
            midi = nearest_midi_in_range(pc, prev, lo, hi)
        else:
            midi = choose_open_string_friendly(candidates, prev) if prefer_open else min(candidates, key=lambda x: abs(x - prev))
        step, alter, octv = midi_to_pitch(midi)
        m.append(xml_note(step, alter, octv, dur_eighth, voice=1, note_type="eighth"))
        prev = midi
    verify_measure_duration(m, total)
    return m, prev

def make_phrase_bar(tune: TuneSpec, pcs: List[int], start_midi: int, lo: int, hi: int,
                    rhythm: List[int], prefer_open: bool = False,
                    wide: bool = False) -> Tuple[ET.Element, int]:
    """
    Fill one bar with a specified rhythm pattern (durations in divisions),
    selecting notes from pcs. Optionally use wider leaps.
    """
    m = ET.Element("measure")
    total = tune.divisions_per_measure
    assert sum(rhythm) == total, "Rhythm must fill the bar exactly"

    prev = start_midi
    idx = 0
    for dur in rhythm:
        pc = pcs[idx % len(pcs)]
        candidates = [mi for mi in range(lo, hi + 1) if mi % 12 == pc]
        if not candidates:
            midi = nearest_midi_in_range(pc, prev, lo, hi)
        else:
            if prefer_open:
                midi = choose_open_string_friendly(candidates, prev)
            else:
                if wide:
                    # prefer leaps: choose a candidate that is farther (but not insane)
                    midi = max(candidates, key=lambda x: min(abs(x - prev), 14))
                else:
                    midi = min(candidates, key=lambda x: abs(x - prev))
        step, alter, octv = midi_to_pitch(midi)
        m.append(xml_note(step, alter, octv, dur, voice=1, note_type=note_type_from_duration(tune.divisions_per_quarter, dur)))
        prev = midi
        idx += 1
    verify_measure_duration(m, total)
    return m, prev

def make_two_voice_counterpoint_bar(tune: TuneSpec,
                                    upper_pcs: List[int],
                                    lower_pcs: List[int],
                                    upper_start: int,
                                    lower_start: int,
                                    lo_upper: int, hi_upper: int,
                                    lo_lower: int, hi_lower: int,
                                    motion: str) -> Tuple[ET.Element, int, int]:
    """
    Create one measure with two voices.
    motion: 'contrary', 'oblique', 'parallel', 'free'
    We'll write quarter notes (Orbit: 3 quarters; Crystal: 4 quarters) per voice.
    """
    m = ET.Element("measure")
    total = tune.divisions_per_measure
    q = tune.divisions_per_quarter
    count = total // q

    upper = upper_start
    lower = lower_start

    # Voice 1 (upper)
    for i in range(count):
        pc = upper_pcs[i % len(upper_pcs)]
        upper = nearest_midi_in_range(pc, upper, lo_upper, hi_upper)
        step, alter, octv = midi_to_pitch(upper)
        m.append(xml_note(step, alter, octv, q, voice=1, note_type="quarter"))

    # Backup
    m.append(xml_backup(total))

    # Voice 2 (lower)
    for i in range(count):
        if motion == "oblique":
            # hold bass for first half then move
            if i < count // 2:
                pc = lower_pcs[0]
            else:
                pc = lower_pcs[(i - count // 2) % len(lower_pcs)]
        elif motion == "parallel":
            # simple parallel by keeping same index relationship (but different register)
            pc = lower_pcs[i % len(lower_pcs)]
        elif motion == "contrary":
            # reverse indexing
            pc = lower_pcs[(-i - 1) % len(lower_pcs)]
        else:
            pc = lower_pcs[(i * 2) % len(lower_pcs)]

        lower = nearest_midi_in_range(pc, lower, lo_lower, hi_lower)
        step, alter, octv = midi_to_pitch(lower)
        m.append(xml_note(step, alter, octv, q, voice=2, note_type="quarter"))

    verify_measure_duration(m, total)
    return m, upper, lower

# -----------------------------
# Tune definitions
# -----------------------------

ORBIT = TuneSpec(
    name="Orbit",
    short="Orbit",
    base_dir=r"C:\Users\mike\Documents\Cursor AI Projects\GCE-Jazz\Trio Tunes\Tune02_Orbit\Practice",
    key_fifths=-1,  # F major
    tempo_qpm=160,
    time=TimeSig(3, 4),
)

CRYSTAL = TuneSpec(
    name="Crystal Silence",
    short="Crystal_Silence",
    base_dir=r"C:\Users\mike\Documents\Cursor AI Projects\GCE-Jazz\Trio Tunes\Tune11_Crystal_Silence\Practice",
    key_fifths=3,  # A major
    tempo_qpm=80,
    time=TimeSig(4, 4),
)

# Progression definitions (internal)
ORBIT_CHORDS = [
    ("F", "lyd"), ("Eb", "lyd_aug"), ("Db", "lyd"), ("B", "lyd"),
    ("Bb", "dor"), ("Ab", "lyd"), ("Gb", "lyd"), ("E", "lyd"),
    ("F", "lyd"), ("Db", "lyd"), ("A", "lyd"), ("G", "lyd"),
    ("F", "lyd"), ("Eb", "dor"), ("Db", "lyd"), ("F", "lyd"),
]

CRYSTAL_CHORDS = [
    ("A", "lyd"), ("F#", "aeo"), ("D", "lyd"), ("E", "mix"),
    ("A", "lyd"), ("C#", "aeo"), ("B", "dor"), ("E", "mix"),
    ("F", "lyd"), ("G", "lyd"), ("A", "lyd"), ("D", "lyd"),
    ("B", "dor"), ("E", "mix"), ("A", "lyd"), ("A", "lyd"),
]

def chord_pc_pool(root: str, mode: str) -> List[int]:
    if mode == "lyd":
        return lydian_pc_set(root)
    if mode == "lyd_aug":
        return lydian_aug_pc_set(root)
    if mode == "dor":
        return dorian_pc_set(root)
    if mode == "aeo":
        # Aeolian = natural minor
        root_pc = name_to_pc(root)
        intervals = [0, 2, 3, 5, 7, 8, 10]
        return [(root_pc + i) % 12 for i in intervals]
    if mode == "mix":
        # Mixolydian
        root_pc = name_to_pc(root)
        intervals = [0, 2, 4, 5, 7, 9, 10]
        return [(root_pc + i) % 12 for i in intervals]
    raise ValueError(f"Unknown mode {mode}")

# Triad pair pools
ORBIT_TRIAD_PAIRS = {
    "Diatonic": [("F", "maj"), ("G", "maj")],           # F/G (Lydian)
    "Lydian":   [("F", "maj"), ("G", "maj")],           # same, emphasise #4 colour via scale tones
    "Minor":    [("D", "min"), ("A", "min")],           # relative-ish flavor (keeps floating)
    "Applied":  [("F", "maj"), ("G", "maj")],           # applied per bar via chord roots, below
}

CRYSTAL_TRIAD_PAIRS = {
    "Diatonic": [("A", "maj"), ("B", "maj")],           # A/B (Lydian)
    "Lydian":   [("A", "maj"), ("B", "maj")],
    "Minor":    [("F#", "min"), ("A", "maj")],          # F#m/A
    "Applied":  [("A", "maj"), ("B", "maj")],           # applied per bar via chord roots, below
}

def triad_pair_pc_pool(pair: List[Tuple[str, str]]) -> List[int]:
    pcs: List[int] = []
    for root, qual in pair:
        pcs += triad_pc_set(root, "aug" if qual == "aug" else ("min" if qual == "min" else "maj"))
    # unique but stable order
    seen = set()
    out = []
    for pc in pcs:
        if pc not in seen:
            out.append(pc)
            seen.add(pc)
    return out

# -----------------------------
# File generators per category
# -----------------------------

def gen_triadpairs(tune: TuneSpec) -> Dict[str, List[ET.Element]]:
    """
    4 files:
    01 diatonic (8 bars)
    02 lydian (8 bars)
    03 minor (8 bars)
    04 applied (16 bars, follows progression)
    """
    lo, hi = (50, 76) if tune is ORBIT else (59, 91)  # Crystal raised 1 octave
    start = 62 if tune is ORBIT else 76  # Crystal raised 1 octave (around E5)

    if tune is ORBIT:
        pairs = ORBIT_TRIAD_PAIRS
        prog = ORBIT_CHORDS
        prefer_open = False
    else:
        pairs = CRYSTAL_TRIAD_PAIRS
        prog = CRYSTAL_CHORDS
        prefer_open = True

    out: Dict[str, List[ET.Element]] = {}

    # 8-bar patterns for first three
    for key, fname in [
        ("Diatonic", "TriadPair_01_Diatonic"),
        ("Lydian", "TriadPair_02_Lydian"),
        ("Minor", "TriadPair_03_Minor"),
    ]:
        pc_pool = triad_pair_pc_pool(pairs[key])
        measures = []
        prev = start
        for _ in range(8):
            m, prev = make_eighth_arpeggio_bar(tune, pc_pool, prev, lo, hi, prefer_open=prefer_open)
            measures.append(m)
        out[fname] = measures

    # Applied: 16 bars, adapt pool per bar from progression root (still triad-pair style)
    measures = []
    prev = start
    for (root, mode) in prog:
        # Build a bar pool: (triad on root) + (triad on lydian II if major-ish, or dorian IV if minor-ish)
        if mode in ("dor", "aeo"):
            # minor context: root min + bIII maj (colour) -> avoids functional pull
            root_tri = triad_pc_set(root, "min")
            bIII_root_pc = (name_to_pc(root) + 3) % 12
            bIII_step, bIII_alter = SEMITONE_TO_STEP_ALTER[bIII_root_pc]
            bIII_name = bIII_step + ("b" if bIII_alter == -1 else ("#" if bIII_alter == 1 else ""))
            color_tri = triad_pc_set(bIII_name, "maj")
            pc_pool = list(dict.fromkeys(root_tri + color_tri))
        else:
            # major/lyd context: root maj + II maj
            root_tri = triad_pc_set(root, "maj")
            II_root_pc = (name_to_pc(root) + 2) % 12
            II_step, II_alter = SEMITONE_TO_STEP_ALTER[II_root_pc]
            II_name = II_step + ("b" if II_alter == -1 else ("#" if II_alter == 1 else ""))
            II_tri = triad_pc_set(II_name, "maj")
            pc_pool = list(dict.fromkeys(root_tri + II_tri))
        m, prev = make_eighth_arpeggio_bar(tune, pc_pool, prev, lo, hi, prefer_open=prefer_open)
        measures.append(m)
    out["TriadPair_04_Applied"] = measures

    return out

def gen_phrases(tune: TuneSpec) -> Dict[str, List[ET.Element]]:
    """
    5 files, each 2–4 bars:
    Opening (bars 1–4): 4 bars
    Middle (bars 5–8): 4 bars
    Bridge (bars 9–12): 4 bars
    Closing (bars 13–16): 4 bars
    Connectors: 4 bars (barline-spilling tendency)
    """
    lo, hi = (52, 79) if tune is ORBIT else (50, 81)
    start = 67 if tune is ORBIT else 64
    prefer_open = tune is CRYSTAL

    prog = ORBIT_CHORDS if tune is ORBIT else CRYSTAL_CHORDS

    # rhythm patterns (sum to measure)
    if tune is ORBIT:
        # 3/4 => 48 divisions
        q = tune.divisions_per_quarter
        rhythms = [
            [q, q, q],                                   # 3 quarters
            [q, q//2, q//2, q],                           # quarter, 2 eighths, quarter
            [q//2, q//2, q, q],                           # 2 eighths, 2 quarters
            [q, q, q//2, q//2],                           # 2 quarters, 2 eighths
        ]
    else:
        # 4/4 => 64 divisions
        q = tune.divisions_per_quarter
        rhythms = [
            [2*q, q, q],                                  # half + 2 quarters
            [q, q, q, q],                                  # 4 quarters
            [q, q//2, q//2, q, q],                         # quarter + 2 eighths + 2 quarters
            [q//2, q//2, q, q, q],                         # 2 eighths + 3 quarters
        ]

    def make_phrase(bars: List[int], wide: bool = False) -> List[ET.Element]:
        measures: List[ET.Element] = []
        prev = start
        for bi, bar_index in enumerate(bars):
            root, mode = prog[bar_index]
            pcs = chord_pc_pool(root, mode)
            rhythm = rhythms[(bi + bar_index) % len(rhythms)]
            m, prev = make_phrase_bar(tune, pcs, prev, lo, hi, rhythm, prefer_open=prefer_open, wide=wide)
            measures.append(m)
        return measures

    out: Dict[str, List[ET.Element]] = {}
    out["Phrase_01_Opening"] = make_phrase([0, 1, 2, 3], wide=(tune is ORBIT))
    out["Phrase_02_Middle"]  = make_phrase([4, 5, 6, 7], wide=(tune is ORBIT))
    out["Phrase_03_Bridge"]  = make_phrase([8, 9, 10, 11], wide=(tune is ORBIT))
    out["Phrase_04_Closing"] = make_phrase([12, 13, 14, 15], wide=(tune is ORBIT))

    # Connectors: encourage barline-spill with longer values
    # We mimic by using fewer notes (more halves) and bigger leaps for Orbit; for Crystal, open-string friendly.
    out["Phrase_05_Connectors"] = make_phrase([3, 4, 7, 8], wide=True)

    return out

def gen_etudes(tune: TuneSpec) -> Dict[str, List[ET.Element]]:
    """
    4 files, each full 16 bars:
    01 Melody (motivic development)
    02 Rhythm (displacement / syncopation)
    03 Intervals (wide intervals)
    04 Dynamics (pp->mp shaping via density; no actual dynamic marks needed)
    """
    lo, hi = (50, 81) if tune is ORBIT else (47, 83)
    start = 66 if tune is ORBIT else 64
    prefer_open = tune is CRYSTAL
    prog = ORBIT_CHORDS if tune is ORBIT else CRYSTAL_CHORDS

    q = tune.divisions_per_quarter
    total = tune.divisions_per_measure

    def bar_rhythm_melodic(i: int) -> List[int]:
        if tune is ORBIT:
            # 3/4 (48): quarter + 2 eighths + quarter
            return [q, q//2, q//2, q]
        else:
            # 4/4 (64): half + quarter + quarter
            return [2*q, q, q]

    def bar_rhythm_rhythmic(i: int) -> List[int]:
        # more syncopation (still simple)
        if tune is ORBIT:
            # 48: 2 eighths + quarter + quarter = 8+8+16+16 = 48
            return [q//2, q//2, q, q]
        else:
            # 64: quarter + 2 eighths + quarter + quarter = 16+8+8+16+16 = 64
            return [q, q//2, q//2, q, q]

    def bar_rhythm_sparse(i: int) -> List[int]:
        if tune is ORBIT:
            return [2*q, q]  # half + quarter
        else:
            return [2*q, 2*q]  # two halves

    def make_etude(kind: str) -> List[ET.Element]:
        measures: List[ET.Element] = []
        prev = start
        for i, (root, mode) in enumerate(prog):
            pcs = chord_pc_pool(root, mode)
            if kind == "Melody":
                rhythm = bar_rhythm_melodic(i)
                wide = False
            elif kind == "Rhythm":
                rhythm = bar_rhythm_rhythmic(i)
                wide = False
            elif kind == "Intervals":
                rhythm = bar_rhythm_melodic(i)
                wide = True
            elif kind == "Dynamics":
                # shape by density: sparse early, more notes mid, sparse at end
                if i < 4 or i > 11:
                    rhythm = bar_rhythm_sparse(i)
                else:
                    rhythm = bar_rhythm_melodic(i)
                wide = False
            else:
                raise ValueError(kind)

            m, prev = make_phrase_bar(
                tune, pcs, prev, lo, hi, rhythm,
                prefer_open=prefer_open, wide=wide
            )
            measures.append(m)
        return measures

    return {
        "Etude_01_Melody": make_etude("Melody"),
        "Etude_02_Rhythm": make_etude("Rhythm"),
        "Etude_03_Intervals": make_etude("Intervals"),
        "Etude_04_Dynamics": make_etude("Dynamics"),
    }

def gen_counterpoint(tune: TuneSpec) -> Dict[str, List[ET.Element]]:
    """
    4 files, 8–16 bars each:
    01 Contrary (8 bars)
    02 Oblique (8 bars)
    03 Parallel (8 bars)
    04 Free (16 bars)
    Two voices on one staff using <backup>.
    """
    prog = ORBIT_CHORDS if tune is ORBIT else CRYSTAL_CHORDS
    prefer_open = tune is CRYSTAL

    lo_upper, hi_upper = (60, 84) if tune is ORBIT else (62, 88)
    lo_lower, hi_lower = (45, 62) if tune is ORBIT else (40, 60)

    upper_start = 72 if tune is ORBIT else 76
    lower_start = 52 if tune is ORBIT else 45  # A2-ish for Crystal drones

    def pools_for_bar(root: str, mode: str) -> Tuple[List[int], List[int]]:
        pcs = chord_pc_pool(root, mode)
        # upper voice tends to color tones (avoid too-rooty)
        upper = [pcs[i] for i in [2, 3, 5, 6, 1] if i < len(pcs)]
        # lower voice tends to stable tones (root/5/2)
        lower = [pcs[i] for i in [0, 4, 1, 6] if i < len(pcs)]
        return upper, lower

    def make_cp(motion: str, bars: int) -> List[ET.Element]:
        measures: List[ET.Element] = []
        up = upper_start
        lo = lower_start
        for i in range(bars):
            root, mode = prog[i % len(prog)]
            upper_pcs, lower_pcs = pools_for_bar(root, mode)

            # Crystal: encourage drones/oblique by biasing lower_pcs toward A/E
            if prefer_open:
                a_pc = name_to_pc("A")
                e_pc = name_to_pc("E")
                lower_pcs = [a_pc, e_pc] + lower_pcs

            m, up, lo = make_two_voice_counterpoint_bar(
                tune,
                upper_pcs=upper_pcs,
                lower_pcs=lower_pcs,
                upper_start=up,
                lower_start=lo,
                lo_upper=lo_upper, hi_upper=hi_upper,
                lo_lower=lo_lower, hi_lower=hi_lower,
                motion=motion
            )
            measures.append(m)
        return measures

    return {
        "Counterpoint_01_Contrary": make_cp("contrary", 8),
        "Counterpoint_02_Oblique":  make_cp("oblique", 8),
        "Counterpoint_03_Parallel": make_cp("parallel", 8),
        "Counterpoint_04_Free":     make_cp("free", 16),
    }

# -----------------------------
# File orchestration
# -----------------------------

SUBDIRS = ["TriadPairs", "Phrases", "Etudes", "Counterpoint"]

def generate_for_tune(tune: TuneSpec) -> List[str]:
    generated_paths: List[str] = []

    # Ensure subdirs
    for sd in SUBDIRS:
        os.makedirs(os.path.join(tune.base_dir, sd), exist_ok=True)

    # Build content maps
    triadpairs = gen_triadpairs(tune)
    phrases = gen_phrases(tune)
    etudes = gen_etudes(tune)
    counterpoint = gen_counterpoint(tune)

    plan: List[Tuple[str, str, Dict[str, List[ET.Element]]]] = [
        ("TriadPairs", f"{tune.short}_", triadpairs),
        ("Phrases", f"{tune.short}_", phrases),
        ("Etudes", f"{tune.short}_", etudes),
        ("Counterpoint", f"{tune.short}_", counterpoint),
    ]

    for subdir, prefix, dct in plan:
        for stem, measures in dct.items():
            title = f"{tune.name} — {stem.replace('_', ' ')}"
            filename = f"{prefix}{stem}.musicxml"
            path = os.path.join(tune.base_dir, subdir, filename)

            # Add attributes+tempo on first measure of each file
            if measures:
                add_attributes_and_tempo(measures[0], tune)

            # Verify all measures and write
            expected = tune.divisions_per_measure
            for mi, m in enumerate(measures, start=1):
                try:
                    verify_measure_duration(m, expected)
                except Exception as e:
                    raise RuntimeError(f"{tune.short} {stem} measure {mi} failed duration check: {e}") from e

            write_musicxml(path, title, tune, measures)
            print(f"[OK] Wrote: {path}")
            generated_paths.append(path)

    return generated_paths

def main() -> None:
    print("Generating practice exercises (34 MusicXML files total)...")
    all_paths: List[str] = []
    for tune in [ORBIT, CRYSTAL]:
        print(f"\n=== {tune.name} ===")
        paths = generate_for_tune(tune)
        all_paths.extend(paths)

    # Final counts
    print("\n=== SUMMARY ===")
    print(f"Total files generated: {len(all_paths)} (expected 34)")
    if len(all_paths) != 34:
        raise SystemExit("ERROR: Expected 34 files. Check generation logs.")
    print("All files generated successfully.")

if __name__ == "__main__":
    main()

