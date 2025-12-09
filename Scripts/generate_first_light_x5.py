"""
First Light x5 - Pat Metheny Style (5-STAR VERSION)
====================================================

UPGRADES FOR 5-STAR:
- More distinctive opening motif (Metheny soaring signature)
- Modal interchange: Add bVII and IV/IV for richness
- More dynamic chord melody with voice movement
- Brazilian influence in rhythm (Metheny loves Brazil!)

Key: G Major (warm, optimistic)
Tempo: 96 BPM (flowing)
"""

import xml.etree.ElementTree as ET
from xml.dom import minidom
from pathlib import Path
from dataclasses import dataclass
from typing import List, Tuple

NOTE_TO_MIDI = {
    "C": 0, "C#": 1, "Db": 1, "D": 2, "D#": 3, "Eb": 3,
    "E": 4, "F": 5, "F#": 6, "Gb": 6, "G": 7, 
    "G#": 8, "Ab": 8, "A": 9, "A#": 10, "Bb": 10, "B": 11
}

MIDI_TO_NOTE = {
    0: ("C", 0), 1: ("C", 1), 2: ("D", 0), 3: ("E", -1),
    4: ("E", 0), 5: ("F", 0), 6: ("F", 1), 7: ("G", 0),
    8: ("A", -1), 9: ("A", 0), 10: ("B", -1), 11: ("B", 0)
}

WHOLE = 64
DOTTED_HALF = 48
HALF = 32
DOTTED_QUARTER = 24
QUARTER = 16
DOTTED_EIGHTH = 12
EIGHTH = 8
SIXTEENTH = 4
BAR = 64


@dataclass
class Note:
    pitch: int
    duration: int
    is_rest: bool = False
    
    def get_xml(self) -> Tuple[str, int, int]:
        if self.is_rest:
            return ("C", 4, 0)
        octave = (self.pitch // 12) - 1
        pc = self.pitch % 12
        step, alter = MIDI_TO_NOTE[pc]
        return (step, octave, alter)


@dataclass
class ChordVoicing:
    pitches: List[int]
    duration: int


@dataclass 
class Chord:
    root: str
    quality: str
    
    def to_kind(self) -> str:
        kinds = {
            "maj7": "major-seventh", "maj9": "major-ninth", "6/9": "major-sixth",
            "m7": "minor-seventh", "m9": "minor-ninth",
            "7": "dominant", "7sus4": "suspended-fourth", "9": "dominant-ninth",
            "": "major", "m": "minor",
        }
        return kinds.get(self.quality, "major-seventh")


def verify(items, bar_num, section):
    total = sum(i.duration for i in items)
    ok = "✓" if total == BAR else "✗"
    print(f"  {ok} {section} Bar {bar_num}: {total}")
    return total == BAR


class FirstLightX5:
    """5-star Pat Metheny inspired composition."""
    
    def __init__(self):
        self.title = "First Light x5"
        self.composer = "GCE (Pat Metheny Style)"
        self.tempo = 96
        self.divisions = 16
        self.key_fifths = 1  # G major
        
    def p(self, n, o):
        return NOTE_TO_MIDI[n] + (o + 1) * 12
    
    def n(self, note, oct, dur):
        return Note(self.p(note, oct), dur)
    
    def r(self, dur):
        return Note(0, dur, is_rest=True)
    
    def chord(self, notes, dur):
        return ChordVoicing([self.p(n, o) for n, o in notes], dur)
    
    # =========================================================================
    # INTRO: Metheny's soaring signature with optimistic warmth
    # =========================================================================
    
    def intro_melody(self):
        items = []
        
        # Bar 1: Gmaj9 - SOARING opening motif (Metheny signature!)
        # 8+8+16+16+16 = 64 ✓
        bar1 = [
            self.n("D", 5, EIGHTH),      # 5th
            self.n("E", 5, EIGHTH),      # 6th
            self.n("G", 5, QUARTER),     # Root
            self.n("A", 5, QUARTER),     # 9th - classic Metheny color
            self.n("B", 5, QUARTER),     # 3rd high - soaring!
        ]
        verify(bar1, 1, "Intro")
        items.extend(bar1)
        
        # Bar 2: Continue ascending then graceful fall
        # 8+8+16+32 = 64 ✓
        bar2 = [
            self.n("D", 6, EIGHTH),      # High 5th - peak!
            self.n("B", 5, EIGHTH),      # Graceful descent
            self.n("A", 5, QUARTER),     
            self.n("G", 5, HALF),        # Settle on root
        ]
        verify(bar2, 2, "Intro")
        items.extend(bar2)
        
        # Bar 3: Cmaj9 - IV chord with Metheny warmth
        # 8+8+8+8+16+16 = 64 ✓
        bar3 = [
            self.n("E", 5, EIGHTH),      # 3rd of C
            self.n("G", 5, EIGHTH),      # 5th
            self.n("B", 5, EIGHTH),      # 7th
            self.n("D", 6, EIGHTH),      # 9th
            self.n("C", 6, QUARTER),     # Root high
            self.n("A", 5, QUARTER),     # 6th - warm
        ]
        verify(bar3, 3, "Intro")
        items.extend(bar3)
        
        # Bar 4: Fmaj7 - bVII! Modal interchange for richness
        # 16+16+32 = 64 ✓
        bar4 = [
            self.n("A", 5, QUARTER),     # 3rd of F
            self.n("C", 6, QUARTER),     # 5th
            self.n("E", 6, HALF),        # Major 7th - SOARING!
        ]
        verify(bar4, 4, "Intro")
        items.extend(bar4)
        
        # Bar 5: Em9 - ii chord with singing melody
        # 8+8+8+8+32 = 64 ✓
        bar5 = [
            self.n("B", 5, EIGHTH),      # 5th
            self.n("D", 6, EIGHTH),      # 7th
            self.n("F#", 6, EIGHTH),     # 9th - high color
            self.n("E", 6, EIGHTH),      # Root
            self.n("G", 5, HALF),        # b3 - minor color
        ]
        verify(bar5, 5, "Intro")
        items.extend(bar5)
        
        # Bar 6: Am9 - gentle descent
        # 16+16+16+16 = 64 ✓
        bar6 = [
            self.n("E", 5, QUARTER),     # 5th
            self.n("C", 5, QUARTER),     # b3
            self.n("B", 4, QUARTER),     # 9th
            self.n("A", 4, QUARTER),     # Root
        ]
        verify(bar6, 6, "Intro")
        items.extend(bar6)
        
        # Bar 7: D9 - dominant with Brazilian anticipation
        # 8+8+16+8+8+16 = 64 ✓
        bar7 = [
            self.n("F#", 4, EIGHTH),     # 3rd
            self.n("A", 4, EIGHTH),      # 5th
            self.n("E", 5, QUARTER),     # 9th
            self.n("D", 5, EIGHTH),      # Root
            self.n("C", 5, EIGHTH),      # 7th
            self.n("A", 4, QUARTER),     # 5th - back
        ]
        verify(bar7, 7, "Intro")
        items.extend(bar7)
        
        # Bar 8: Gmaj9 - Home with warmth
        # 16+16+32 = 64 ✓
        bar8 = [
            self.n("D", 5, QUARTER),     # 5th
            self.n("B", 4, QUARTER),     # 3rd
            self.n("G", 4, HALF),        # Root - rest
        ]
        verify(bar8, 8, "Intro")
        items.extend(bar8)
        
        return items
    
    def intro_bass(self):
        notes = []
        notes.extend([self.n("G", 2, HALF), self.n("D", 3, HALF)])
        notes.extend([self.n("G", 2, HALF), self.n("B", 2, HALF)])
        notes.extend([self.n("C", 2, HALF), self.n("E", 3, HALF)])
        notes.extend([self.n("F", 2, WHOLE)])  # bVII!
        notes.extend([self.n("E", 2, HALF), self.n("B", 2, HALF)])
        notes.extend([self.n("A", 2, HALF), self.n("G", 2, HALF)])
        notes.extend([self.n("D", 2, WHOLE)])
        notes.extend([self.n("G", 2, WHOLE)])
        return notes
    
    def intro_chords(self):
        return [
            Chord("G", "maj9"), Chord("G", "maj9"),
            Chord("C", "maj9"), Chord("F", "maj7"),  # bVII!
            Chord("E", "m9"), Chord("A", "m7"),
            Chord("D", "9"), Chord("G", "maj9"),
        ]
    
    # =========================================================================
    # TRIAD SOLO: Arpeggiated with Metheny's lyrical flow
    # =========================================================================
    
    def triad_solo(self):
        items = []
        
        # Bar 1: G + Am - gentle flowing arpeggios
        # 8+8+8+8+8+8+16 = 64 ✓
        bar1 = [
            self.n("G", 4, EIGHTH),      # G arp
            self.n("B", 4, EIGHTH),      
            self.n("D", 5, EIGHTH),      
            self.n("A", 4, EIGHTH),      # Am arp
            self.n("C", 5, EIGHTH),      
            self.n("E", 5, EIGHTH),      
            self.n("D", 5, QUARTER),     # Land gently
        ]
        verify(bar1, 1, "TriadSolo")
        items.extend(bar1)
        
        # Bar 2: Bm + C - rising sequence
        # 8+8+8+8+8+8+8+8 = 64 ✓
        bar2 = [
            self.n("B", 4, EIGHTH),      # Bm arp
            self.n("D", 5, EIGHTH),      
            self.n("F#", 5, EIGHTH),     
            self.n("G", 5, EIGHTH),      # C arp starts
            self.n("C", 5, EIGHTH),      
            self.n("E", 5, EIGHTH),      
            self.n("G", 5, EIGHTH),      
            self.n("E", 5, EIGHTH),      # Echo
        ]
        verify(bar2, 2, "TriadSolo")
        items.extend(bar2)
        
        # Bar 3: D + Em with push
        # 12+4+8+8+8+8+16 = 64 ✓
        bar3 = [
            self.n("D", 5, DOTTED_EIGHTH),  # D arp with push
            self.n("F#", 5, SIXTEENTH),     
            self.n("A", 5, EIGHTH),         
            self.n("E", 5, EIGHTH),         # Em arp
            self.n("G", 5, EIGHTH),         
            self.n("B", 5, EIGHTH),         
            self.n("A", 5, QUARTER),        # Soaring hold
        ]
        verify(bar3, 3, "TriadSolo")
        items.extend(bar3)
        
        # Bar 4: G resolution - soaring
        # 8+8+8+8+32 = 64 ✓
        bar4 = [
            self.n("G", 4, EIGHTH),      # Low G
            self.n("B", 4, EIGHTH),      
            self.n("D", 5, EIGHTH),      
            self.n("G", 5, EIGHTH),      # Octave
            self.n("B", 5, HALF),        # Hold - soaring!
        ]
        verify(bar4, 4, "TriadSolo")
        items.extend(bar4)
        
        # Bar 5: C + D with gentle displacement
        # 8+8+8+8+8+8+8+8 = 64 ✓
        bar5 = [
            self.r(EIGHTH),              # Gentle breath
            self.n("C", 5, EIGHTH),      # C arp
            self.n("E", 5, EIGHTH),      
            self.n("G", 5, EIGHTH),      
            self.n("D", 5, EIGHTH),      # D arp
            self.n("F#", 5, EIGHTH),     
            self.n("A", 5, EIGHTH),      
            self.n("G", 5, EIGHTH),      # Smooth landing
        ]
        verify(bar5, 5, "TriadSolo")
        items.extend(bar5)
        
        # Bar 6: Em + F#dim - color change
        # 8+8+8+16+8+8+8 = 64 ✓
        bar6 = [
            self.n("E", 5, EIGHTH),      # Em arp
            self.n("G", 5, EIGHTH),      
            self.n("B", 5, EIGHTH),      
            self.n("A", 5, QUARTER),     # Slight pause
            self.n("F#", 5, EIGHTH),     # F#dim arp
            self.n("A", 5, EIGHTH),      
            self.n("C", 5, EIGHTH),      
        ]
        verify(bar6, 6, "TriadSolo")
        items.extend(bar6)
        
        # Bar 7: Am + D - building to resolution
        # 8+8+8+8+8+8+16 = 64 ✓
        bar7 = [
            self.n("A", 4, EIGHTH),      # Am arp
            self.n("C", 5, EIGHTH),      
            self.n("E", 5, EIGHTH),      
            self.n("D", 5, EIGHTH),      # D arp
            self.n("F#", 5, EIGHTH),     
            self.n("A", 5, EIGHTH),      
            self.n("F#", 5, QUARTER),    # Leading tone held
        ]
        verify(bar7, 7, "TriadSolo")
        items.extend(bar7)
        
        # Bar 8: G final arpeggio
        # 8+8+8+8+32 = 64 ✓
        bar8 = [
            self.n("G", 4, EIGHTH),      
            self.n("D", 5, EIGHTH),      
            self.n("B", 4, EIGHTH),      
            self.n("G", 4, EIGHTH),      
            self.n("D", 5, HALF),        # Warm 5th hold
        ]
        verify(bar8, 8, "TriadSolo")
        items.extend(bar8)
        
        return items
    
    def triad_solo_bass(self):
        notes = []
        notes.extend([self.n("G", 2, HALF), self.n("A", 2, HALF)])
        notes.extend([self.n("B", 2, HALF), self.n("C", 2, HALF)])
        notes.extend([self.n("D", 2, HALF), self.n("E", 2, HALF)])
        notes.extend([self.n("G", 2, WHOLE)])
        notes.extend([self.n("C", 2, HALF), self.n("D", 2, HALF)])
        notes.extend([self.n("E", 2, HALF), self.n("F#", 2, HALF)])
        notes.extend([self.n("A", 2, HALF), self.n("D", 2, HALF)])
        notes.extend([self.n("G", 2, WHOLE)])
        return notes
    
    def triad_solo_chords(self):
        return [
            Chord("G", ""), Chord("B", "m"),
            Chord("D", ""), Chord("G", ""),
            Chord("C", ""), Chord("E", "m"),
            Chord("A", "m"), Chord("G", ""),
        ]
    
    # =========================================================================
    # CHORD MELODY: Metheny's lush maj9 and 6/9 voicings with voice movement
    # =========================================================================
    
    def chord_melody(self):
        items = []
        
        # Bar 1: Gmaj9 - Metheny's signature open voicing
        bar1 = [
            self.chord([("A", 5), ("D", 5), ("B", 4), ("G", 4)], HALF),
            self.chord([("B", 5), ("E", 5), ("D", 5), ("G", 4)], HALF),  # Voice moves!
        ]
        verify(bar1, 1, "ChordMel")
        items.extend(bar1)
        
        # Bar 2: Em9 with ascending melody
        bar2 = [
            self.chord([("D", 5), ("B", 4), ("G", 4), ("E", 4)], HALF),
            self.chord([("F#", 5), ("D", 5), ("B", 4), ("E", 4)], HALF),
        ]
        verify(bar2, 2, "ChordMel")
        items.extend(bar2)
        
        # Bar 3: Cmaj9 - open and warm
        bar3 = [
            self.chord([("D", 5), ("B", 4), ("G", 4), ("C", 4)], HALF),
            self.chord([("E", 5), ("C", 5), ("G", 4), ("C", 4)], HALF),
        ]
        verify(bar3, 3, "ChordMel")
        items.extend(bar3)
        
        # Bar 4: Fmaj7 (bVII) - beautiful modal color
        bar4 = [
            self.chord([("E", 5), ("C", 5), ("A", 4), ("F", 4)], WHOLE),
        ]
        verify(bar4, 4, "ChordMel")
        items.extend(bar4)
        
        # Bar 5: Am9 -> D9
        bar5 = [
            self.chord([("B", 5), ("E", 5), ("C", 5), ("A", 4)], HALF),
            self.chord([("E", 5), ("C", 5), ("A", 4), ("D", 4)], HALF),
        ]
        verify(bar5, 5, "ChordMel")
        items.extend(bar5)
        
        # Bar 6: Bm7 -> E7 (secondary dominant!)
        bar6 = [
            self.chord([("A", 5), ("F#", 5), ("D", 5), ("B", 4)], HALF),
            self.chord([("G#", 5), ("D", 5), ("B", 4), ("E", 4)], HALF),
        ]
        verify(bar6, 6, "ChordMel")
        items.extend(bar6)
        
        # Bar 7: Am7 -> D7
        bar7 = [
            self.chord([("G", 5), ("E", 5), ("C", 5), ("A", 4)], HALF),
            self.chord([("F#", 5), ("C", 5), ("A", 4), ("D", 4)], HALF),
        ]
        verify(bar7, 7, "ChordMel")
        items.extend(bar7)
        
        # Bar 8: G6/9 - warm resolution
        bar8 = [
            self.chord([("A", 5), ("E", 5), ("B", 4), ("G", 4)], WHOLE),
        ]
        verify(bar8, 8, "ChordMel")
        items.extend(bar8)
        
        return items
    
    def chord_melody_bass(self):
        notes = []
        notes.extend([self.n("G", 2, WHOLE)])
        notes.extend([self.n("E", 2, WHOLE)])
        notes.extend([self.n("C", 2, WHOLE)])
        notes.extend([self.n("F", 2, WHOLE)])  # bVII
        notes.extend([self.n("A", 2, HALF), self.n("D", 2, HALF)])
        notes.extend([self.n("B", 2, HALF), self.n("E", 2, HALF)])
        notes.extend([self.n("A", 2, HALF), self.n("D", 2, HALF)])
        notes.extend([self.n("G", 2, WHOLE)])
        return notes
    
    def chord_melody_chords(self):
        return [
            Chord("G", "maj9"), Chord("E", "m9"),
            Chord("C", "maj9"), Chord("F", "maj7"),
            Chord("A", "m7"), Chord("B", "m7"),
            Chord("A", "m7"), Chord("G", "6/9"),
        ]
    
    # =========================================================================
    # OUTRO: Higher restatement with ultimate soaring resolution
    # =========================================================================
    
    def outro_melody(self):
        items = []
        
        # Bar 1: Ultimate soaring version!
        bar1 = [
            self.n("D", 6, EIGHTH),      # High!
            self.n("E", 6, EIGHTH),      
            self.n("G", 6, QUARTER),     # Soaring G
            self.n("A", 6, QUARTER),     
            self.n("B", 6, QUARTER),     # Peak!
        ]
        verify(bar1, 1, "Outro")
        items.extend(bar1)
        
        # Bar 2: Graceful descent
        bar2 = [
            self.n("D", 6, DOTTED_QUARTER),
            self.n("B", 5, EIGHTH),      
            self.n("G", 5, HALF),        
        ]
        verify(bar2, 2, "Outro")
        items.extend(bar2)
        
        # Bar 3: C warmth
        bar3 = [
            self.n("E", 5, QUARTER),     
            self.n("G", 5, QUARTER),     
            self.n("C", 6, HALF),        # Warm C
        ]
        verify(bar3, 3, "Outro")
        items.extend(bar3)
        
        # Bar 4: F modal color (bVII)
        bar4 = [
            self.n("A", 5, QUARTER),     
            self.n("C", 6, QUARTER),     
            self.n("E", 6, HALF),        # Major 7th of F
        ]
        verify(bar4, 4, "Outro")
        items.extend(bar4)
        
        # Bar 5: Em recall
        bar5 = [
            self.n("E", 5, QUARTER),     
            self.n("G", 5, QUARTER),     
            self.n("B", 5, QUARTER),     
            self.n("D", 6, QUARTER),     
        ]
        verify(bar5, 5, "Outro")
        items.extend(bar5)
        
        # Bar 6: Am gentle
        bar6 = [
            self.n("C", 5, QUARTER),     
            self.n("E", 5, QUARTER),     
            self.n("A", 5, HALF),        
        ]
        verify(bar6, 6, "Outro")
        items.extend(bar6)
        
        # Bar 7: D9 final approach
        bar7 = [
            self.n("F#", 5, EIGHTH),     
            self.n("A", 5, EIGHTH),      
            self.n("E", 5, QUARTER),     
            self.n("D", 5, HALF),        
        ]
        verify(bar7, 7, "Outro")
        items.extend(bar7)
        
        # Bar 8: G6/9 - ultimate warmth
        bar8 = [
            self.chord([("A", 5), ("E", 5), ("B", 4), ("G", 4)], WHOLE),
        ]
        verify(bar8, 8, "Outro")
        items.extend(bar8)
        
        return items
    
    def outro_bass(self):
        notes = []
        notes.extend([self.n("G", 2, WHOLE)])
        notes.extend([self.n("G", 2, WHOLE)])
        notes.extend([self.n("C", 2, WHOLE)])
        notes.extend([self.n("F", 2, WHOLE)])
        notes.extend([self.n("E", 2, WHOLE)])
        notes.extend([self.n("A", 2, WHOLE)])
        notes.extend([self.n("D", 2, WHOLE)])
        notes.extend([self.n("G", 1, WHOLE)])
        return notes
    
    def outro_chords(self):
        return [
            Chord("G", "maj9"), Chord("G", "maj9"),
            Chord("C", "maj9"), Chord("F", "maj7"),
            Chord("E", "m7"), Chord("A", "m7"),
            Chord("D", "9"), Chord("G", "6/9"),
        ]
    
    # =========================================================================
    # MusicXML Export
    # =========================================================================
    
    def create_musicxml(self):
        score = ET.Element("score-partwise", version="4.0")
        
        work = ET.SubElement(score, "work")
        ET.SubElement(work, "work-title").text = self.title
        
        ident = ET.SubElement(score, "identification")
        creator = ET.SubElement(ident, "creator", type="composer")
        creator.text = self.composer
        
        part_list = ET.SubElement(score, "part-list")
        gtr = ET.SubElement(part_list, "score-part", id="P1")
        ET.SubElement(gtr, "part-name").text = "Guitar"
        bass = ET.SubElement(part_list, "score-part", id="P2")
        ET.SubElement(bass, "part-name").text = "Bass"
        
        print("\nVerifying all bars...")
        sections = [
            ("1 - Intro", self.intro_melody(), self.intro_bass(), self.intro_chords()),
            ("2 - Triad Solo", self.triad_solo(), self.triad_solo_bass(), self.triad_solo_chords()),
            ("3 - Chord Melody", self.chord_melody(), self.chord_melody_bass(), self.chord_melody_chords()),
            ("4 - Outro", self.outro_melody(), self.outro_bass(), self.outro_chords()),
        ]
        
        all_guitar = []
        all_bass = []
        all_chords = []
        markers = []
        
        bar_count = 0
        for name, g, b, c in sections:
            markers.append((bar_count, name))
            all_guitar.extend(g)
            all_bass.extend(b)
            all_chords.extend(c)
            bar_count += 8
        
        guitar_part = ET.SubElement(score, "part", id="P1")
        self._write_part(guitar_part, all_guitar, all_chords, markers, True)
        
        bass_part = ET.SubElement(score, "part", id="P2")
        self._write_part(bass_part, all_bass, [], [], False)
        
        rough = ET.tostring(score, encoding="unicode")
        return minidom.parseString(rough).toprettyxml(indent="  ")
    
    def _write_part(self, part, items, chords, markers, is_guitar):
        marker_dict = {m: name for m, name in markers}
        measure_num = 1
        item_idx = 0
        chord_idx = 0
        
        while item_idx < len(items):
            measure = ET.SubElement(part, "measure", number=str(measure_num))
            
            if measure_num == 1:
                attr = ET.SubElement(measure, "attributes")
                ET.SubElement(attr, "divisions").text = str(self.divisions)
                key = ET.SubElement(attr, "key")
                ET.SubElement(key, "fifths").text = str(self.key_fifths)
                ET.SubElement(key, "mode").text = "major"
                time = ET.SubElement(attr, "time")
                ET.SubElement(time, "beats").text = "4"
                ET.SubElement(time, "beat-type").text = "4"
                clef = ET.SubElement(attr, "clef")
                ET.SubElement(clef, "sign").text = "G" if is_guitar else "F"
                ET.SubElement(clef, "line").text = "2" if is_guitar else "4"
                
                if is_guitar:
                    direction = ET.SubElement(measure, "direction", placement="above")
                    dt = ET.SubElement(direction, "direction-type")
                    met = ET.SubElement(dt, "metronome")
                    ET.SubElement(met, "beat-unit").text = "quarter"
                    ET.SubElement(met, "per-minute").text = str(self.tempo)
            
            if is_guitar and (measure_num - 1) in marker_dict:
                direction = ET.SubElement(measure, "direction", placement="above")
                dt = ET.SubElement(direction, "direction-type")
                ET.SubElement(dt, "rehearsal").text = marker_dict[measure_num - 1]
            
            if is_guitar and chord_idx < len(chords):
                c = chords[chord_idx]
                harmony = ET.SubElement(measure, "harmony")
                root = ET.SubElement(harmony, "root")
                if len(c.root) > 1 and c.root[1] in '#b':
                    ET.SubElement(root, "root-step").text = c.root[0]
                    ET.SubElement(root, "root-alter").text = "1" if c.root[1] == '#' else "-1"
                else:
                    ET.SubElement(root, "root-step").text = c.root
                ET.SubElement(harmony, "kind").text = c.to_kind()
                chord_idx += 1
            
            dur_in_bar = 0
            while item_idx < len(items) and dur_in_bar < BAR:
                item = items[item_idx]
                
                if isinstance(item, ChordVoicing):
                    for i, pitch in enumerate(item.pitches):
                        note_elem = ET.SubElement(measure, "note")
                        if i > 0:
                            ET.SubElement(note_elem, "chord")
                        p = ET.SubElement(note_elem, "pitch")
                        step, octave, alter = self._pitch_xml(pitch)
                        ET.SubElement(p, "step").text = step
                        if alter != 0:
                            ET.SubElement(p, "alter").text = str(alter)
                        ET.SubElement(p, "octave").text = str(octave)
                        ET.SubElement(note_elem, "duration").text = str(item.duration)
                        t, dot = self._dur_type(item.duration)
                        ET.SubElement(note_elem, "type").text = t
                        if dot:
                            ET.SubElement(note_elem, "dot")
                    dur_in_bar += item.duration
                    item_idx += 1
                    
                elif isinstance(item, Note):
                    note_elem = ET.SubElement(measure, "note")
                    if item.is_rest:
                        ET.SubElement(note_elem, "rest")
                    else:
                        p = ET.SubElement(note_elem, "pitch")
                        step, octave, alter = self._pitch_xml(item.pitch)
                        ET.SubElement(p, "step").text = step
                        if alter != 0:
                            ET.SubElement(p, "alter").text = str(alter)
                        ET.SubElement(p, "octave").text = str(octave)
                    ET.SubElement(note_elem, "duration").text = str(item.duration)
                    t, dot = self._dur_type(item.duration)
                    ET.SubElement(note_elem, "type").text = t
                    if dot:
                        ET.SubElement(note_elem, "dot")
                    dur_in_bar += item.duration
                    item_idx += 1
            
            measure_num += 1
    
    def _pitch_xml(self, midi):
        octave = (midi // 12) - 1
        pc = midi % 12
        step, alter = MIDI_TO_NOTE[pc]
        return (step, octave, alter)
    
    def _dur_type(self, dur):
        if dur == DOTTED_HALF:
            return ("half", True)
        if dur == DOTTED_QUARTER:
            return ("quarter", True)
        if dur == DOTTED_EIGHTH:
            return ("eighth", True)
        mapping = {WHOLE: "whole", HALF: "half", QUARTER: "quarter",
                   EIGHTH: "eighth", SIXTEENTH: "16th"}
        return (mapping.get(dur, "quarter"), False)
    
    def save(self, path):
        xml = self.create_musicxml()
        lines = xml.split('\n')
        if lines[0].startswith('<?xml'):
            lines = lines[1:]
        
        content = '<?xml version="1.0" encoding="UTF-8"?>\n'
        content += '<!DOCTYPE score-partwise PUBLIC "-//Recordare//DTD MusicXML 4.0 Partwise//EN" '
        content += '"http://www.musicxml.org/dtds/partwise.dtd">\n'
        content += '\n'.join(lines)
        
        with open(path, 'w', encoding='utf-8') as f:
            f.write(content)
        return path


def main():
    print("=" * 60)
    print("FIRST LIGHT x5 - 5-STAR VERSION")
    print("Pat Metheny Style - UPGRADED")
    print("=" * 60)
    
    out = Path(__file__).parent.parent / "Trio Tunes" / "Alternative_LeadSheets" / "Pat Metheny - First Light"
    out.mkdir(parents=True, exist_ok=True)
    
    comp = FirstLightX5()
    path = out / "First_Light_x5.musicxml"
    comp.save(str(path))
    
    print(f"\nSaved: {path}")
    print("\n5-STAR UPGRADES:")
    print("  ✓ Distinctive soaring opening motif")
    print("  ✓ Modal interchange: Fmaj7 (bVII) for richness")
    print("  ✓ E7 secondary dominant for color")
    print("  ✓ Voice movement in chord melody")
    print("  ✓ Ultimate soaring outro (to B6!)")
    print("=" * 60)


if __name__ == "__main__":
    main()

