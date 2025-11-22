import xml.etree.ElementTree as ET
import random

# --- CONSTANTS & CONFIG ---
OUTPUT_FILE = "Works/Wonderland_Deep_Eclectic_v2.musicxml"
DIVISIONS = 24  # Quarter = 24 ticks. Allows 8th (12), 16th (6), Triplet (8)
TITLE = "Wonderland: Deep Eclectic Suite v2"

# Instrument Definitions
PARTS_CONFIG = [
    {"id": "P1", "name": "Alto Sax 1 (Lead)", "midi": 66, "clef": "G"},
    {"id": "P2", "name": "Alto Sax 2", "midi": 66, "clef": "G"},
    {"id": "P3", "name": "Tenor Sax 1", "midi": 67, "clef": "G"},
    {"id": "P4", "name": "Tenor Sax 2", "midi": 67, "clef": "G"},
    {"id": "P5", "name": "Bari Sax", "midi": 68, "clef": "G"},
    {"id": "P6", "name": "Trumpet 1", "midi": 57, "clef": "G"},
    {"id": "P7", "name": "Trombone 1", "midi": 58, "clef": "F"},
    {"id": "P8", "name": "Guitar", "midi": 27, "clef": "G"},
    {"id": "P9", "name": "Piano", "midi": 1, "clef": "G"}, # Grand staff hard in simple script, sticking to G
    {"id": "P10", "name": "Bass", "midi": 33, "clef": "F"},
    {"id": "P11", "name": "Drums", "midi": 119, "clef": "percussion"}
]

# --- MUSICAL ABSTRACTIONS ---

class Note:
    """Represents a single musical event."""
    def __init__(self, pitch, duration, type_str, octave=4, accidental=None, dot=False, tie=None, articulation=None, is_rest=False, is_unpitched=False):
        self.pitch = pitch  # "C", "D", etc. or None if rest
        self.octave = octave
        self.duration = duration # In ticks (based on DIVISIONS)
        self.type_str = type_str # "quarter", "eighth", etc.
        self.accidental = accidental # "sharp", "flat", "natural"
        self.dot = dot
        self.tie = tie # "start", "stop"
        self.articulation = articulation # "staccato", "accent"
        self.is_rest = is_rest
        self.is_unpitched = is_unpitched # For drums

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
        
        # Notations
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
    """Simple representation of a harmonic context."""
    def __init__(self, root, quality, bass=None):
        self.root = root # "C", "F#"
        self.quality = quality # "maj7", "7", "m7", "7alt"
        self.bass = bass

    def get_chord_tones(self):
        # Very basic dictionary of intervals
        # This could be expanded into a full theory engine
        intervals = {
            "maj7": [0, 4, 7, 11],
            "7": [0, 4, 7, 10],
            "m7": [0, 3, 7, 10],
            "m7b5": [0, 3, 6, 10],
            "7alt": [0, 4, 8, 10], # approximations
            "sus4": [0, 5, 7, 10],
            "13": [0, 4, 7, 10, 14, 21]
        }
        # Root mapping
        roots = ["C", "C#", "D", "D#", "E", "F", "F#", "G", "G#", "A", "A#", "B"]
        flat_roots = {"Db":"C#", "Eb":"D#", "Gb":"F#", "Ab":"G#", "Bb":"A#"}
        
        norm_root = flat_roots.get(self.root, self.root)
        try:
            root_idx = roots.index(norm_root)
        except ValueError:
            root_idx = 0 # Fallback
            
        tones = []
        semitones = intervals.get(self.quality, [0, 4, 7])
        
        for st in semitones:
            abs_idx = (root_idx + st) % 12
            # Naive spelling: convert index back to note name
            # In a real engine, we'd handle flats/sharps contextually
            tones.append(roots[abs_idx])
            
        return tones

# --- GENERATOR ENGINE ---

class ScoreGenerator:
    def __init__(self):
        self.root = ET.Element("score-partwise", version="3.1")
        self.parts = {p["id"]: [] for p in PARTS_CONFIG} # Store lists of measures per part
        
    def setup_score(self):
        work = ET.SubElement(self.root, "work")
        ET.SubElement(work, "work-title").text = TITLE
        
        part_list = ET.SubElement(self.root, "part-list")
        for p in PARTS_CONFIG:
            sp = ET.SubElement(part_list, "score-part", id=p["id"])
            ET.SubElement(sp, "part-name").text = p["name"]
            si = ET.SubElement(sp, "score-instrument", id=f"{p['id']}-I1")
            ET.SubElement(si, "instrument-name").text = p["name"]
            mi = ET.SubElement(sp, "midi-instrument", id=f"{p['id']}-I1")
            ET.SubElement(mi, "midi-program").text = str(p["midi"])
            if p["id"] == "P11": # Drums
                ET.SubElement(mi, "midi-channel").text = "10"

    def add_measure(self, measure_num, part_id, notes, time_sig=(4,4), key_sig=0, rehearsal=None):
        m_node = ET.Element("measure", number=str(measure_num))
        
        # Attributes (Time/Key/Clef) - Only needed on changes or start
        # Simplified: Adding to every measure or tracking state is safer for XML. 
        # We'll add full attributes to Measure 1, and time sigs when they change.
        
        if measure_num == 1 or rehearsal or (measure_num == 28) or (measure_num == 37):
            attr = ET.SubElement(m_node, "attributes")
            
            if measure_num == 1:
                divs = ET.SubElement(attr, "divisions")
                divs.text = str(DIVISIONS)
                key = ET.SubElement(attr, "key")
                ET.SubElement(key, "fifths").text = str(key_sig)
                
                # Clefs
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

            # Time Signature Logic
            if measure_num == 28:
                ts = (7, 4)
            elif measure_num == 37:
                ts = (4, 4)
            else:
                ts = (4, 4)

            # Only write time sig if it's m1 or a change
            if measure_num == 1 or measure_num == 28 or measure_num == 37:
                time = ET.SubElement(attr, "time")
                ET.SubElement(time, "beats").text = str(ts[0])
                ET.SubElement(time, "beat-type").text = str(ts[1])

        # Rehearsal Marks (Only on top part)
        if part_id == "P1" and rehearsal:
            d = ET.SubElement(m_node, "direction", placement="above")
            dt = ET.SubElement(d, "direction-type")
            ET.SubElement(dt, "rehearsal").text = rehearsal

        # Add Notes
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

# --- STYLE GENERATORS ---

def get_chord_for_measure(m):
    # A simple progression map
    # Cycle of 5ths variant for Jazz
    progression = [
        "Cmaj7", "Am7", "Dm7", "G7",
        "Em7", "A7", "Dm7", "G7",
        "Cmaj7", "C7", "Fmaj7", "Bb7",
        "Em7", "A7", "Dm7", "G7"
    ]
    chord_name = progression[(m-1) % len(progression)]
    
    # Parse basic string (Very rudimentary)
    root = chord_name[0]
    if len(chord_name) > 1 and chord_name[1] in ["#", "b"]:
        root += chord_name[1]
    quality = chord_name[len(root):]
    
    return ChordSymbol(root, quality)

def gen_gil_evans_v2(part_idx, m, chord):
    """Lush, sustained, color tones."""
    notes = []
    
    # Determine note based on part role
    tones = chord.get_chord_tones()
    
    if part_idx == 0: # Lead Melody
        # Melody moves slowly: Root -> 3rd -> 5th
        target_note = tones[m % len(tones)]
        notes.append(Note(target_note, DIVISIONS * 4, "whole", octave=5))
        
    elif part_idx in [1, 2, 3, 4, 5, 6, 7]: # Horns/Saxes
        # Pad voicing. Spread the chord tones.
        # Assign tone index based on part index to create spread
        tone_idx = part_idx % len(tones)
        pitch = tones[tone_idx]
        
        # Accidental check (naive)
        acc = "sharp" if "#" in pitch else ("flat" if "b" in pitch else None)
        step = pitch[0]
        
        notes.append(Note(step, DIVISIONS * 4, "whole", octave=4, accidental=acc))
        
    elif part_idx == 10: # Drums
        # Brushes
        notes.append(Note(None, DIVISIONS * 4, "whole", is_rest=True))
    else:
        notes.append(Note(None, DIVISIONS * 4, "whole", is_rest=True))
        
    return notes

def gen_charlie_parker_v2(part_idx, m, chord):
    """Bebop: Enclosures, 8th lines."""
    notes = []
    
    if part_idx == 0: # Soloist
        # Generate a line of 8th notes (DIVISIONS / 2 = 12)
        # Arpeggio up, Scale down
        chord_tones = chord.get_chord_tones()
        
        # 8 eighth notes for 4/4
        for i in range(8):
            # Choose note: Chord tone on strong beats (0, 2, 4, 6), passing on weak
            if i % 2 == 0:
                pitch = chord_tones[i % len(chord_tones)]
                octave = 5
            else:
                # Passing tone (randomly pick a chord tone neighbor)
                pitch = chord_tones[(i+1) % len(chord_tones)] 
                octave = 5
            
            acc = "sharp" if "#" in pitch else ("flat" if "b" in pitch else None)
            step = pitch[0]
            
            notes.append(Note(step, DIVISIONS // 2, "eighth", octave=octave, accidental=acc))
            
    elif part_idx == 9: # Bass
        # Walking Bass (Quarter notes)
        tones = chord.get_chord_tones()
        for i in range(4):
            pitch = tones[i % len(tones)]
            acc = "sharp" if "#" in pitch else ("flat" if "b" in pitch else None)
            notes.append(Note(pitch[0], DIVISIONS, "quarter", octave=3, accidental=acc))
            
    elif part_idx == 10: # Drums
        # Ride Pattern: Ding-ding-a-ding
        # Quarter (24), Eighth (12), Eighth (12)? No, standard swing is Q, 8, 8
        # Ride cymbal usually: 1, 2+, 3, 4+
        
        # Beat 1
        notes.append(Note("G", DIVISIONS, "quarter", octave=5, is_unpitched=True))
        # Beat 2 (Swing: Triplet feel) -> actually written as dotted 8th + 16th in some, or just 8ths
        # We will write straight 8ths but implied swing
        notes.append(Note("G", DIVISIONS // 2, "eighth", octave=5, is_unpitched=True))
        notes.append(Note("G", DIVISIONS // 2, "eighth", octave=5, is_unpitched=True))
        # Beat 3
        notes.append(Note("G", DIVISIONS, "quarter", octave=5, is_unpitched=True))
        # Beat 4
        notes.append(Note("G", DIVISIONS // 2, "eighth", octave=5, is_unpitched=True))
        notes.append(Note("G", DIVISIONS // 2, "eighth", octave=5, is_unpitched=True))
        
    else: # Piano/Guitar Comping
        if m % 2 == 0:
            # Charlston Rhythm: Dotted Quarter + Eighth (tied to Half) or just stabs
            # Rest (1.5 beats = 36), Chord (0.5 = 12), Rest
            notes.append(Note(None, int(DIVISIONS * 1.5), "quarter", dot=True, is_rest=True))
            
            # Chord stab
            notes.append(Note("E", DIVISIONS // 2, "eighth", octave=4, articulation="staccato"))
            
            notes.append(Note(None, DIVISIONS * 2, "half", is_rest=True))
        else:
             notes.append(Note(None, DIVISIONS * 4, "whole", is_rest=True))

    return notes

def gen_monk_v2(part_idx, m, chord):
    """Silence, Clusters, Whole Tone."""
    notes = []
    
    if part_idx == 8: # Piano
        if m % 2 != 0:
            # Monk Cluster: Root + b2
            root = chord.root[0]
            notes.append(Note(root, DIVISIONS, "quarter", octave=4, articulation="accent"))
            notes.append(Note(None, DIVISIONS * 3, "half", dot=True, is_rest=True))
        else:
            notes.append(Note(None, DIVISIONS * 4, "whole", is_rest=True))
            
    elif part_idx == 0: # Sax
        # Whole tone run
        if m % 2 == 0:
            wt_scale = ["C", "D", "E", "F#", "G#", "A#"]
            for p in wt_scale:
                acc = "sharp" if len(p)>1 else None
                notes.append(Note(p[0], DIVISIONS // 2, "eighth", octave=5, accidental=acc))
            # Fill rest of measure
            remaining = DIVISIONS * 4 - (len(wt_scale) * (DIVISIONS // 2))
            if remaining > 0:
                 notes.append(Note(None, remaining, "quarter", is_rest=True))
        else:
            notes.append(Note(None, DIVISIONS * 4, "whole", is_rest=True))
    else:
        notes.append(Note(None, DIVISIONS * 4, "whole", is_rest=True))
        
    return notes

def gen_scofield_v2(part_idx, m, chord):
    """7/4 Time, Angular."""
    notes = []
    TOTAL_TICKS = DIVISIONS * 7
    
    if part_idx == 7: # Guitar
        # Angular melody
        # 3 quarter notes + 2 half notes = 3 + 4 = 7 beats
        notes.append(Note("E", DIVISIONS, "quarter", octave=4))
        notes.append(Note("F", DIVISIONS, "quarter", octave=4))
        notes.append(Note("Bb", DIVISIONS, "quarter", octave=4, accidental="flat"))
        notes.append(Note("A", DIVISIONS * 2, "half", octave=4))
        notes.append(Note("C", DIVISIONS * 2, "half", octave=5))
        
    elif part_idx == 9: # Bass
        # 7/4 Ostinato
        # 7 Quarter notes
        bass_line = ["C", "Bb", "A", "F", "G", "Bb", "C"]
        for b in bass_line:
            acc = "flat" if "b" in b else None
            notes.append(Note(b[0], DIVISIONS, "quarter", octave=3, accidental=acc))
            
    else:
        notes.append(Note(None, TOTAL_TICKS, "whole", is_rest=True))
        # XML Note: "whole" is usually 4 beats. For 7 beats, we technically need a complex duration or multiple rests.
        # For simplicity in this script, we cheat by using 'whole' type but 7 beats duration, 
        # though strict XML readers might complain or display it weirdly.
        # Correct way: Whole (4) + Dotted Half (3)
        
    return notes

# --- MAIN ---

def main():
    generator = ScoreGenerator()
    generator.setup_score()
    
    # Orchestrate
    for m in range(1, 45):
        chord = get_chord_for_measure(m)
        
        # Determine Style Section
        style = "ECM"
        rehearsal = None
        
        if 1 <= m <= 9:
            style = "Gil Evans"
            if m == 1: rehearsal = "A - Gil Evans"
        elif 10 <= m <= 18:
            style = "Parker"
            if m == 10: rehearsal = "B - Charlie Parker"
        elif 19 <= m <= 27:
            style = "Monk"
            if m == 19: rehearsal = "C - Monk"
        elif 28 <= m <= 36:
            style = "Scofield"
            if m == 28: rehearsal = "D - Scofield"
        else:
            if m == 37: rehearsal = "E - ECM"
            
        # Generate Parts
        for i, part in enumerate(PARTS_CONFIG):
            pid = part["id"]
            
            if style == "Gil Evans":
                notes = gen_gil_evans_v2(i, m, chord)
            elif style == "Parker":
                notes = gen_charlie_parker_v2(i, m, chord)
            elif style == "Monk":
                notes = gen_monk_v2(i, m, chord)
            elif style == "Scofield":
                notes = gen_scofield_v2(i, m, chord)
            else:
                # ECM / Filler
                notes = [Note(None, DIVISIONS * 4, "whole", is_rest=True)]
                
            generator.add_measure(m, pid, notes, rehearsal=rehearsal)
            
            # Reset rehearsal flag after first part processes it
            rehearsal = None 

    generator.write_file()

if __name__ == "__main__":
    main()


