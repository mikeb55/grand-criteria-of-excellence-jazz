import xml.etree.ElementTree as ET
import random
import math

# --- CONSTANTS & CONFIG ---
OUTPUT_FILE = "Works/V4_Wonderland.musicxml"
DIVISIONS = 24  # Quarter = 24 ticks
TITLE = "Wonderland V4: Parker Variations"

# Instrument Definitions (Bebop Quintet + Guitar)
PARTS_CONFIG = [
    {"id": "P1", "name": "Alto Sax (Lead)", "midi": 65, "clef": "G"}, 
    {"id": "P2", "name": "Trumpet", "midi": 56, "clef": "G"},
    {"id": "P3", "name": "Tenor Sax", "midi": 66, "clef": "G"},
    {"id": "P4", "name": "Piano", "midi": 0, "clef": "G"}, 
    {"id": "P5", "name": "Guitar", "midi": 26, "clef": "G"},
    {"id": "P6", "name": "Upright Bass", "midi": 32, "clef": "F"},
    {"id": "P7", "name": "Drum Kit", "midi": 119, "clef": "percussion"}
]

# --- MUSICAL THEORY UTILS ---
NOTES = ["C", "C#", "D", "D#", "E", "F", "F#", "G", "G#", "A", "A#", "B"]

class Note:
    def __init__(self, pitch, duration, type_str, octave=4, accidental=None, dot=False, tie=None, articulation=None, is_rest=False, is_unpitched=False):
        self.pitch = pitch
        self.octave = octave
        self.duration = duration
        self.type_str = type_str
        self.accidental = accidental
        self.dot = dot
        self.tie = tie
        self.articulation = articulation
        self.is_rest = is_rest
        self.is_unpitched = is_unpitched

    def to_xml(self):
        n = ET.Element("note")
        if self.is_rest:
            ET.SubElement(n, "rest")
        elif self.is_unpitched:
             p = ET.SubElement(n, "unpitched")
             ET.SubElement(p, "display-step").text = self.pitch
             ET.SubElement(p, "display-octave").text = str(self.octave)
        else:
            p = ET.SubElement(n, "pitch")
            ET.SubElement(p, "step").text = self.pitch
            ET.SubElement(p, "octave").text = str(self.octave)
            if self.accidental:
                alter_val = "1" if self.accidental == "sharp" else "-1"
                if self.accidental == "natural": alter_val = "0"
                ET.SubElement(p, "alter").text = alter_val
                ET.SubElement(n, "accidental").text = self.accidental

        ET.SubElement(n, "duration").text = str(self.duration)
        ET.SubElement(n, "type").text = self.type_str
        if self.dot: ET.SubElement(n, "dot")
        
        if self.tie or self.articulation:
            notations = ET.SubElement(n, "notations")
            if self.tie:
                ET.SubElement(n, "tie", type=self.tie)
                ET.SubElement(notations, "tied", type=self.tie)
            if self.articulation:
                arts = ET.SubElement(notations, "articulations")
                ET.SubElement(arts, self.articulation)
        return n

class ChordSymbol:
    def __init__(self, root, quality, bass=None):
        self.root = root
        self.quality = quality
        self.bass = bass

    def get_chord_tones(self):
        # Basic chord tone intervals (semitones from root)
        intervals = {
            "maj7": [0, 4, 7, 11],
            "7": [0, 4, 7, 10],
            "m7": [0, 3, 7, 10],
            "m7b5": [0, 3, 6, 10],
            "dim7": [0, 3, 6, 9]
        }
        # Normalize root
        flat_map = {"Bb":"A#", "Eb":"D#", "Ab":"G#", "Db":"C#", "Gb":"F#"}
        norm_root = flat_map.get(self.root, self.root)
        try:
            root_idx = NOTES.index(norm_root)
        except:
            root_idx = 0

        tones = []
        semitones = intervals.get(self.quality, [0, 4, 7])
        for st in semitones:
            idx = (root_idx + st) % 12
            n = NOTES[idx]
            acc = "sharp" if "#" in n else ("flat" if "b" in n else None)
            tones.append({"step": n[0], "acc": acc, "full": n})
        return tones

    def get_bebop_scale(self):
        # Basic Bebop dominant scale logic (approx)
        root_idx = NOTES.index(self.root) if self.root in NOTES else 0
        # Mixolydian + major 7 passing tone
        intervals = [0, 2, 4, 5, 7, 9, 10, 11] 
        scale = []
        for i in intervals:
            idx = (root_idx + i) % 12
            n = NOTES[idx]
            acc = "sharp" if "#" in n else ("flat" if "b" in n else None)
            scale.append({"step": n[0], "acc": acc})
        return scale

# --- PARKER ENGINES ---

def gen_ornithology_style(part_idx, m, chord):
    """
    Inspired by 'Ornithology'
    Motif: Descending triplet pickup, High-arching arpeggios.
    """
    notes = []
    tones = chord.get_chord_tones()
    
    # LEAD (Alto)
    if part_idx == 0: 
        if m % 2 == 0:
            # "The Pick Up" - Triplet run into beat 1
            # Just simulate the landing
            target = tones[0] # Root
            notes.append(Note(target["step"], DIVISIONS, "quarter", octave=5, accidental=target["acc"], articulation="accent"))
            # Rest
            notes.append(Note(None, DIVISIONS*3, "half", dot=True, is_rest=True))
        else:
            # Arpeggio Up (Quarter notes)
            for i in range(4):
                t = tones[i % len(tones)]
                notes.append(Note(t["step"], DIVISIONS, "quarter", octave=4 + (i//4), accidental=t["acc"]))
    
    # RHYTHM SECTION (Standard Swing)
    elif part_idx == 5: # Bass
        # Walking Bass
        for i in range(4):
             t = tones[i % len(tones)]
             notes.append(Note(t["step"], DIVISIONS, "quarter", octave=3, accidental=t["acc"]))
    elif part_idx == 6: # Drums
        # Ding-ding-a-ding
        for i in range(4):
            if i in [1, 3]: # 2 and 4
                notes.append(Note("G", DIVISIONS//3 * 2, "quarter", octave=5, is_unpitched=True)) # Triplet swing feel approx
                notes.append(Note("G", DIVISIONS//3, "eighth", octave=5, is_unpitched=True)) 
            else:
                notes.append(Note("G", DIVISIONS, "quarter", octave=5, is_unpitched=True))
    else: # Comping
        if m % 2 != 0:
             notes.append(Note(None, DIVISIONS, "quarter", is_rest=True))
             # Charleston Stab
             notes.append(Note(tones[2]["step"], DIVISIONS, "quarter", octave=4, accidental=tones[2]["acc"], articulation="staccato"))
             notes.append(Note(None, DIVISIONS*2, "half", is_rest=True))
        else:
             notes.append(Note(None, DIVISIONS*4, "whole", is_rest=True))
             
    return notes

def gen_donna_lee_style(part_idx, m, chord):
    """
    Inspired by 'Donna Lee'
    Motif: Chromatic enclosures, 8th note runs starting on offbeats.
    """
    notes = []
    scale = chord.get_bebop_scale()
    
    if part_idx == 0: # Solo
        # Stream of 8ths
        for i in range(8):
            # Contour: Up and Down
            idx = (m * 8 + i) % len(scale)
            n = scale[idx]
            notes.append(Note(n["step"], DIVISIONS//2, "eighth", octave=5, accidental=n["acc"]))
            
    elif part_idx == 5: # Bass
        # Fast Walking
        tones = chord.get_chord_tones()
        for i in range(4):
             t = tones[i % len(tones)]
             notes.append(Note(t["step"], DIVISIONS, "quarter", octave=3, accidental=t["acc"]))
             
    elif part_idx == 6: # Drums
         # Fast Ride
        for i in range(4):
             notes.append(Note("G", DIVISIONS, "quarter", octave=5, is_unpitched=True))
    else:
        notes.append(Note(None, DIVISIONS*4, "whole", is_rest=True))
        
    return notes

def gen_scrapple_style(part_idx, m, chord):
    """
    Inspired by 'Scrapple from the Apple'
    Motif: Rhythmic displacement, repeated riffs on the bridge.
    """
    notes = []
    tones = chord.get_chord_tones()
    
    if part_idx == 0:
        # Riff: 2 8ths + Quarter
        # "Ba-da BAP"
        t1 = tones[2] # 5th
        t2 = tones[0] # Root
        
        notes.append(Note(t1["step"], DIVISIONS//2, "eighth", octave=5, accidental=t1["acc"]))
        notes.append(Note(t1["step"], DIVISIONS//2, "eighth", octave=5, accidental=t1["acc"]))
        notes.append(Note(t2["step"], DIVISIONS, "quarter", octave=5, accidental=t2["acc"], articulation="accent"))
        notes.append(Note(None, DIVISIONS*2, "half", is_rest=True))
        
    elif part_idx == 5:
         # Two-feel (Half notes)
         notes.append(Note(tones[0]["step"], DIVISIONS*2, "half", octave=3, accidental=tones[0]["acc"]))
         notes.append(Note(tones[2]["step"], DIVISIONS*2, "half", octave=3, accidental=tones[2]["acc"]))
    elif part_idx == 6:
         # Brushes
         notes.append(Note(None, DIVISIONS*4, "whole", is_rest=True))
    else:
         notes.append(Note(None, DIVISIONS*4, "whole", is_rest=True))

    return notes

def gen_yardbird_style(part_idx, m, chord):
    """
    Inspired by 'Yardbird Suite'
    Motif: Grace notes, lyrical melody.
    """
    notes = []
    tones = chord.get_chord_tones()
    
    if part_idx == 0:
        # Long note with simulated grace
        # (Grace notes are complex in basic XML gen, we simulate with 32nd pickup)
        if m % 2 != 0:
            # Pickup
            notes.append(Note(tones[1]["step"], DIVISIONS//4, "16th", octave=5, accidental=tones[1]["acc"])) 
            # Landing
            rem = DIVISIONS*4 - (DIVISIONS//4)
            notes.append(Note(tones[2]["step"], rem, "whole", octave=5, accidental=tones[2]["acc"])) # Tied feel
        else:
             notes.append(Note(None, DIVISIONS*4, "whole", is_rest=True))
             
    elif part_idx == 5: # Bass
        for i in range(4):
             t = tones[i % len(tones)]
             notes.append(Note(t["step"], DIVISIONS, "quarter", octave=3, accidental=t["acc"]))
    elif part_idx == 6:
         # Backbeat
         for i in range(4):
             if i in [1, 3]:
                 notes.append(Note("C", DIVISIONS, "quarter", octave=4, is_unpitched=True, articulation="accent")) # Snare
             else:
                 notes.append(Note("G", DIVISIONS, "quarter", octave=5, is_unpitched=True)) # Ride
    else:
        notes.append(Note(None, DIVISIONS*4, "whole", is_rest=True))
        
    return notes


# --- MAIN ENGINE ---

class ScoreGenerator:
    def __init__(self):
        self.root = ET.Element("score-partwise", version="3.1")
        self.parts = {p["id"]: [] for p in PARTS_CONFIG} 
        
    def setup_score(self):
        work = ET.SubElement(self.root, "work")
        ET.SubElement(work, "work-title").text = TITLE
        
        part_list = ET.SubElement(self.root, "part-list")
        for p in PARTS_CONFIG:
            sp = ET.SubElement(part_list, "score-part", id=p["id"])
            ET.SubElement(sp, "part-name").text = p["name"]
            mi = ET.SubElement(sp, "midi-instrument", id=f"{p['id']}-I1")
            ET.SubElement(mi, "midi-program").text = str(p["midi"])
            if p["id"] == "P7": # Drums
                ET.SubElement(mi, "midi-channel").text = "10"

    def add_measure(self, measure_num, part_id, notes, rehearsal=None):
        m_node = ET.Element("measure", number=str(measure_num))
        
        if measure_num == 1 or rehearsal:
            attr = ET.SubElement(m_node, "attributes")
            if measure_num == 1:
                divs = ET.SubElement(attr, "divisions")
                divs.text = str(DIVISIONS)
                key = ET.SubElement(attr, "key")
                ET.SubElement(key, "fifths").text = "0"
                time = ET.SubElement(attr, "time")
                ET.SubElement(time, "beats").text = "4"
                ET.SubElement(time, "beat-type").text = "4"
                
                clef_def = next(p for p in PARTS_CONFIG if p["id"] == part_id)["clef"]
                clef = ET.SubElement(attr, "clef")
                if clef_def == "F":
                    ET.SubElement(clef, "sign").text = "F"
                    ET.SubElement(clef, "line").text = "4"
                elif clef_def == "percussion":
                    ET.SubElement(clef, "sign").text = "percussion"
                    ET.SubElement(clef, "line").text = "2"
                else:
                    ET.SubElement(clef, "sign").text = "G"
                    ET.SubElement(clef, "line").text = "2"

        if part_id == "P1" and rehearsal:
            d = ET.SubElement(m_node, "direction", placement="above")
            dt = ET.SubElement(d, "direction-type")
            ET.SubElement(dt, "rehearsal").text = rehearsal

        for note in notes:
            m_node.append(note.to_xml())
            
        self.parts[part_id].append(m_node)

    def write_file(self):
        for p_conf in PARTS_CONFIG:
            pid = p_conf["id"]
            p_node = ET.SubElement(self.root, "part", id=pid)
            for m in self.parts[pid]:
                p_node.append(m)
                
        tree = ET.ElementTree(self.root)
        ET.indent(tree, space="  ", level=0)
        tree.write(OUTPUT_FILE, encoding="UTF-8", xml_declaration=True)
        print(f"Generated {OUTPUT_FILE}")

def get_chord_for_measure(m):
    # Wonderland Changes
    progression = [
        "Cmaj7", "Am7", "Dm7", "G7",
        "Em7", "A7", "Dm7", "G7",
        "Cmaj7", "F7", "Bb7", "Eb7", 
        "Abmaj7", "Dbmaj7", "Dm7", "G7"
    ]
    chord_name = progression[(m-1) % len(progression)]
    
    # Parser
    root = chord_name[0]
    if len(chord_name) > 1 and chord_name[1] in ["#", "b"]:
        root += chord_name[1]
        quality = chord_name[2:]
    else:
        quality = chord_name[1:]
        
    return ChordSymbol(root, quality)

def main():
    gen = ScoreGenerator()
    gen.setup_score()
    
    # Section Config (4 sections of 12 bars)
    # 1-12: Ornithology
    # 13-24: Donna Lee
    # 25-36: Scrapple from the Apple
    # 37-48: Yardbird Suite
    
    for m in range(1, 49):
        chord = get_chord_for_measure(m)
        rehearsal = None
        style = ""
        
        if 1 <= m <= 12:
            style = "Ornithology"
            if m == 1: rehearsal = "Ornithology (Inspired)"
        elif 13 <= m <= 24:
            style = "Donna Lee"
            if m == 13: rehearsal = "Donna Lee (Inspired)"
        elif 25 <= m <= 36:
            style = "Scrapple"
            if m == 25: rehearsal = "Scrapple from the Apple (Inspired)"
        else:
            style = "Yardbird"
            if m == 37: rehearsal = "Yardbird Suite (Inspired)"
            
        for i, p in enumerate(PARTS_CONFIG):
            if style == "Ornithology":
                notes = gen_ornithology_style(i, m, chord)
            elif style == "Donna Lee":
                notes = gen_donna_lee_style(i, m, chord)
            elif style == "Scrapple":
                notes = gen_scrapple_style(i, m, chord)
            else:
                notes = gen_yardbird_style(i, m, chord)
            
            gen.add_measure(m, p["id"], notes, rehearsal)
            rehearsal = None 

    gen.write_file()

if __name__ == "__main__":
    main()


