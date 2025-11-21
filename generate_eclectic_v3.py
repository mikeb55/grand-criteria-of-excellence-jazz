import xml.etree.ElementTree as ET
import random
import math

# --- CONSTANTS & CONFIG ---
OUTPUT_FILE = "Works/V3_Wonderland.musicxml"
DIVISIONS = 24  # Quarter = 24 ticks
TITLE = "Wonderland: Deep Eclectic Suite V3"

# Instrument Definitions
PARTS_CONFIG = [
    {"id": "P1", "name": "Soprano Sax", "midi": 64, "clef": "G"}, # ECM/Monk leads
    {"id": "P2", "name": "Alto Sax", "midi": 65, "clef": "G"},
    {"id": "P3", "name": "Tenor Sax", "midi": 66, "clef": "G"},
    {"id": "P4", "name": "Bari Sax", "midi": 67, "clef": "G"},
    {"id": "P5", "name": "Trumpet", "midi": 56, "clef": "G"},
    {"id": "P6", "name": "Trombone", "midi": 57, "clef": "F"},
    {"id": "P7", "name": "Elec Guitar", "midi": 27, "clef": "G"},
    {"id": "P8", "name": "Piano", "midi": 0, "clef": "G"}, 
    {"id": "P9", "name": "Upright Bass", "midi": 32, "clef": "F"},
    {"id": "P10", "name": "Drum Kit", "midi": 119, "clef": "percussion"}
]

# --- MUSICAL THEORY UTILS ---

NOTES = ["C", "C#", "D", "D#", "E", "F", "F#", "G", "G#", "A", "A#", "B"]

def get_midi_pitch(note_name, octave):
    """Convert Note Name + Octave to MIDI number."""
    try:
        idx = NOTES.index(note_name)
        return 12 * (octave + 1) + idx
    except:
        return 60

def transpose_note(note_name, semitones):
    """Transpose a note name by semitones."""
    try:
        idx = NOTES.index(note_name)
        new_idx = (idx + semitones) % 12
        return NOTES[new_idx]
    except:
        return note_name

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

    def get_scale(self, scale_type="mixolydian"):
        """Returns a list of notes (pitch, accidental) for the scale."""
        # Normalize flats to sharps for list lookup
        flat_map = {"Bb":"A#", "Eb":"D#", "Ab":"G#", "Db":"C#", "Gb":"F#"}
        norm_root = flat_map.get(self.root, self.root)
        
        try:
            root_idx = NOTES.index(norm_root)
        except:
            root_idx = 0 # Fallback to C
        
        intervals = []
        if scale_type == "whole_tone":
            intervals = [0, 2, 4, 6, 8, 10]
        elif scale_type == "diminished_whole_half":
            intervals = [0, 2, 3, 5, 6, 8, 9, 11]
        elif scale_type == "altered":
            intervals = [0, 1, 3, 4, 6, 8, 10]
        elif scale_type == "lydian":
            intervals = [0, 2, 4, 6, 7, 9, 11]
        elif scale_type == "blues":
            intervals = [0, 3, 5, 6, 7, 10]
        else: # Major/Mixolydian default
            intervals = [0, 2, 4, 5, 7, 9, 10] 
            
        scale = []
        for i in intervals:
            note_idx = (root_idx + i) % 12
            note_name = NOTES[note_idx]
            acc = "sharp" if "#" in note_name else ("flat" if "b" in note_name else None)
            scale.append({"step": note_name[0], "acc": acc, "full": note_name})
        return scale

    def get_quartal_voicing(self):
        """Builds a quartal voicing (stack of 4ths) from the root/mode."""
        # Normalize flats to sharps for list lookup
        flat_map = {"Bb":"A#", "Eb":"D#", "Ab":"G#", "Db":"C#", "Gb":"F#"}
        norm_root = flat_map.get(self.root, self.root)
        
        try:
            root_idx = NOTES.index(norm_root)
        except:
            root_idx = 0

        indices = [0, 5, 10, 15] # 0, 5, 10, 15 semitones approx
        
        voicing = []
        for i in indices:
            note_idx = (root_idx + i) % 12
            note_name = NOTES[note_idx]
            acc = "sharp" if "#" in note_name else ("flat" if "b" in note_name else None)
            voicing.append({"step": note_name[0], "acc": acc})
        return voicing

# --- STYLE GENERATORS ---

def gen_monk_style(part_idx, m, chord):
    """
    Monk Style:
    - Whole Tone Scales
    - Clusters (semitones)
    - Rhythmic displacement & Silence
    - Stride Piano with 'crunch'
    """
    notes = []
    
    # --- PIANO (The Monk Engine) ---
    if part_idx == 7: # Piano (P8 in config is idx 7)
        # Stride Pattern: Root (beat 1), Crunch Chord (beat 2), Root (beat 3), Crunch Chord (beat 4)
        # But Monk often disrupts this.
        
        if m % 4 == 0: # Occasional silence / break
            notes.append(Note(None, DIVISIONS * 4, "whole", is_rest=True))
            return notes

        # Left Hand Root (Low)
        root = chord.root[0]
        root_acc = "sharp" if "#" in chord.root else ("flat" if "b" in chord.root else None)
        
        # Beat 1: Low Root
        notes.append(Note(root, DIVISIONS, "quarter", octave=2, accidental=root_acc, articulation="staccato"))
        
        # Beat 2: Cluster Voicing (e.g., 3rd + 7th + b9)
        # C7 -> E + Bb + Db
        scale = chord.get_scale("diminished_whole_half")
        # Pick random crunch notes
        c1 = scale[2] # ~3rd
        c2 = scale[6] # ~7th
        
        # Write as chord (simulated by just one note in this monophonic engine, or use arpeggio)
        # For this script, we'll just do a dissonant diad if possible, or just one crunchy note
        notes.append(Note(c1["step"], DIVISIONS, "quarter", octave=4, accidental=c1["acc"], articulation="accent"))
        
        # Beat 3: Rest or Root
        if random.random() > 0.5:
             notes.append(Note(None, DIVISIONS, "quarter", is_rest=True))
        else:
             notes.append(Note(root, DIVISIONS, "quarter", octave=2, accidental=root_acc))
             
        # Beat 4: Cluster
        notes.append(Note(c2["step"], DIVISIONS, "quarter", octave=4, accidental=c2["acc"], articulation="staccato"))

    # --- SAXES (Angular Melodies) ---
    elif part_idx == 0: # Soprano Lead
        # Whole Tone Run
        wt = chord.get_scale("whole_tone")
        
        if m % 2 == 0:
            # Descending angular run
            notes.append(Note(None, DIVISIONS, "quarter", is_rest=True)) # Wait count 1
            
            # Triplet feel run
            for _ in range(3):
                n = random.choice(wt)
                notes.append(Note(n["step"], DIVISIONS//3 * 2, "quarter", octave=5, accidental=n["acc"], articulation="accent")) # quarter triplet
                
        else:
            # The "Monk" melody: Root -> b5 -> 6
            notes.append(Note(chord.root[0], DIVISIONS, "quarter", octave=5, articulation="staccato"))
            notes.append(Note(None, DIVISIONS, "quarter", is_rest=True))
            # Leap
            target = wt[3] # Tritione-ish
            notes.append(Note(target["step"], DIVISIONS*2, "half", octave=5, accidental=target["acc"], articulation="accent"))

    # --- DRUMS (Disjointed Swing) ---
    elif part_idx == 9: # Drums
        # Ride cymbal keeps time, Snare drops "bombs"
        # Standard Ride
        notes.append(Note("G", DIVISIONS, "quarter", octave=5, is_unpitched=True)) # 1
        notes.append(Note("G", DIVISIONS//2, "eighth", octave=5, is_unpitched=True)) # 2
        notes.append(Note("G", DIVISIONS//2, "eighth", octave=5, is_unpitched=True)) # +
        
        # Random snare bomb
        if random.random() > 0.7:
             notes.append(Note("C", DIVISIONS, "quarter", octave=4, is_unpitched=True, articulation="accent")) # Snare hit on 3
        else:
             notes.append(Note("G", DIVISIONS, "quarter", octave=5, is_unpitched=True)) # Ride on 3
             
        notes.append(Note("G", DIVISIONS//2, "eighth", octave=5, is_unpitched=True)) # 4
        notes.append(Note("G", DIVISIONS//2, "eighth", octave=5, is_unpitched=True)) # +

    else:
        notes.append(Note(None, DIVISIONS * 4, "whole", is_rest=True))
        
    return notes

def gen_scofield_style(part_idx, m, chord):
    """
    Scofield Style:
    - Inside-Outside playing (Blues scale -> Shifted up semitone -> Back)
    - Funk/Fusion Grooves (16th notes, syncopation)
    - Quartal Harmony stabs
    """
    notes = []
    
    # --- GUITAR (The Sco Sound) ---
    if part_idx == 6: # Elec Guitar
        if m % 2 != 0:
            # Phrase A: "Inside" Blues
            blues = chord.get_scale("blues")
            # Lick: 16th notes
            # Dotted 8th + 16th pattern
            notes.append(Note(blues[0]["step"], int(DIVISIONS * 0.75), "eighth", dot=True, octave=4, accidental=blues[0]["acc"]))
            notes.append(Note(blues[2]["step"], int(DIVISIONS * 0.25), "16th", octave=4, accidental=blues[2]["acc"]))
            
            # Staccato stab
            notes.append(Note(blues[4]["step"], DIVISIONS, "quarter", octave=5, accidental=blues[4]["acc"], articulation="staccato"))
            
            notes.append(Note(None, DIVISIONS * 2, "half", is_rest=True))
            
        else:
            # Phrase B: "Outside" Tension
            # Play phrase a semitone HIGHER than the chord
            # e.g. C7 -> play C# blues lines
            
            # Visualise: C# D# E G# A# ...
            # We will simulate this by shifting the pitch manually
            notes.append(Note(None, DIVISIONS, "quarter", is_rest=True))
            
            # Angular "Outside" Run
            notes.append(Note("C", DIVISIONS//2, "eighth", octave=5, accidental="sharp", articulation="accent")) # Outside root
            notes.append(Note("E", DIVISIONS//2, "eighth", octave=5, accidental="natural"))
            notes.append(Note("F", DIVISIONS//2, "eighth", octave=5, accidental="sharp")) # Outside 4th
            notes.append(Note("B", DIVISIONS//2, "eighth", octave=4, accidental="natural")) # Resolver?
            
            # Resolve "In"
            notes.append(Note("C", DIVISIONS, "quarter", octave=5, accidental="natural", articulation="tenuto"))

    # --- BASS (Funk/Fusion) ---
    elif part_idx == 8: # Bass
        # Syncopated Funk Line
        root = chord.root[0]
        root_acc = "sharp" if "#" in chord.root else ("flat" if "b" in chord.root else None)
        
        # One (heavy)
        notes.append(Note(root, int(DIVISIONS * 0.75), "eighth", dot=True, octave=2, accidental=root_acc, articulation="accent"))
        # e of 1
        notes.append(Note(root, int(DIVISIONS * 0.25), "16th", octave=3, accidental=root_acc))
        
        # Two (rest)
        notes.append(Note(None, DIVISIONS, "quarter", is_rest=True))
        
        # Three (Ghost note / octave)
        notes.append(Note(root, DIVISIONS // 2, "eighth", octave=3, accidental=root_acc, articulation="staccato"))
        notes.append(Note(None, DIVISIONS // 2, "eighth", is_rest=True))
        
        # Four (Walk up)
        notes.append(Note("G", DIVISIONS, "quarter", octave=2))

    # --- DRUMS (Fusion) ---
    elif part_idx == 9: 
        # Tight Hi-Hat Groove
        for i in range(4):
             notes.append(Note("F", DIVISIONS//2, "eighth", octave=5, is_unpitched=True)) # Hi-Hat Closed
             notes.append(Note("F", DIVISIONS//2, "eighth", octave=5, is_unpitched=True))
             
    # --- HORNS (Quartal Pads) ---
    elif part_idx in [1, 2, 5]: # Alto, Tenor, Trombone
        # Sustained quartal chords (background)
        voicing = chord.get_quartal_voicing()
        # Distribute notes
        v_idx = part_idx % len(voicing)
        v_note = voicing[v_idx]
        
        notes.append(Note(v_note["step"], DIVISIONS * 4, "whole", octave=4, accidental=v_note["acc"]))
        
    else:
        notes.append(Note(None, DIVISIONS * 4, "whole", is_rest=True))

    return notes

def gen_ecm_style(part_idx, m, chord):
    """
    ECM Style:
    - Straight 8ths (Euro Jazz)
    - Spacious, Reverb-heavy writing
    - Pedal points
    - Folk-like simple melodies over complex harmonies
    """
    notes = []
    
    # --- PIANO (Keith Jarrett / Lyle Mays style) ---
    if part_idx == 7: 
        # Arpeggiated open chords, lots of sustain
        if m % 2 == 0:
            # Rolling 8ths
            tones = chord.get_scale("lydian")
            # Upward run
            for i in range(8):
                t = tones[i % len(tones)]
                notes.append(Note(t["step"], DIVISIONS//2, "eighth", octave=4 + (i//4), accidental=t["acc"]))
        else:
            # Long chord
            notes.append(Note(chord.root[0], DIVISIONS*4, "whole", octave=3))

    # --- BASS (Eberhard Weber style) ---
    elif part_idx == 8:
        # Singing upper register or low pedal
        if m % 4 == 0:
             # Melodic fill
             notes.append(Note("A", DIVISIONS*2, "half", octave=3))
             notes.append(Note("G", DIVISIONS*2, "half", octave=3))
        else:
             # Low Pedal
             root = chord.root[0]
             notes.append(Note(root, DIVISIONS*4, "whole", octave=2))

    # --- SAX (Jan Garbarek style) ---
    elif part_idx == 0: 
        # Haunting long tones with grace notes (simulated)
        # High register, Lydian #4
        tones = chord.get_scale("lydian")
        sharp4 = tones[3] # The #11
        
        if m % 2 != 0:
            # Long haunting note
            notes.append(Note(sharp4["step"], DIVISIONS*3, "half", dot=True, octave=5, accidental=sharp4["acc"], articulation="tenuto"))
            notes.append(Note(None, DIVISIONS, "quarter", is_rest=True))
        else:
             notes.append(Note(None, DIVISIONS*4, "whole", is_rest=True))

    # --- DRUMS (Jon Christensen style) ---
    elif part_idx == 9:
        # Color, Cymbals, No groove
        # Just random cymbal swells
        if m % 2 == 0:
            notes.append(Note("A", DIVISIONS*4, "whole", octave=5, is_unpitched=True)) # Crash/Ride
        else:
            notes.append(Note(None, DIVISIONS*4, "whole", is_rest=True))
            
    else:
        # Strings / Pads
        notes.append(Note(None, DIVISIONS * 4, "whole", is_rest=True))
        
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
            if p["id"] == "P10": # Drums
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
    # Wonderland Changes (Approx)
    progression = [
        "Cmaj7", "Am7", "Dm7", "G7",
        "Em7", "A7", "Dm7", "G7",
        "Cmaj7", "F7", "Bb7", "Eb7", # Monk bridge feel
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
    
    # Section Config
    # 1-16: Monk (Angular, Whole Tone)
    # 17-32: Scofield (Funk/Fusion, Inside/Outside)
    # 33-48: ECM (Spacious, Lydian)
    
    for m in range(1, 49):
        chord = get_chord_for_measure(m)
        rehearsal = None
        
        if 1 <= m <= 16:
            style = "Monk"
            if m == 1: rehearsal = "A - Monk Style"
        elif 17 <= m <= 32:
            style = "Scofield"
            if m == 17: rehearsal = "B - Scofield Style"
        else:
            style = "ECM"
            if m == 33: rehearsal = "C - ECM Style"
            
        for i, p in enumerate(PARTS_CONFIG):
            if style == "Monk":
                notes = gen_monk_style(i, m, chord)
            elif style == "Scofield":
                notes = gen_scofield_style(i, m, chord)
            else:
                notes = gen_ecm_style(i, m, chord)
            
            gen.add_measure(m, p["id"], notes, rehearsal)
            rehearsal = None # Clear for subsequent parts

    gen.write_file()

if __name__ == "__main__":
    main()

