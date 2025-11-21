import xml.etree.ElementTree as ET
import random

# --- CONFIG ---
OUTPUT_FILE = "Works/V5.2_Wonderland_PianoReduction-Wayne-Shorter.musicxml"
TITLE = "Wonderland V5.2: Shorter Variations (New Motifs)"
DIVISIONS = 24
REDUCTION_PART = {"id": "P1", "name": "Piano", "midi": 0}

NOTES = ["C", "C#", "D", "D#", "E", "F", "F#", "G", "G#", "A", "A#", "B"]

# --- UTILS ---
class Note:
    def __init__(self, pitch, duration, type_str, octave=4, accidental=None, dot=False, tie=None, articulation=None, is_rest=False):
        self.pitch = pitch
        self.duration = duration
        self.type_str = type_str
        self.octave = octave
        self.accidental = accidental
        self.dot = dot
        self.tie = tie
        self.articulation = articulation
        self.is_rest = is_rest

    def to_xml(self):
        n = ET.Element("note")
        if self.is_rest:
            ET.SubElement(n, "rest")
        else:
            p = ET.SubElement(n, "pitch")
            ET.SubElement(p, "step").text = self.pitch
            ET.SubElement(p, "octave").text = str(self.octave)
            if self.accidental:
                alter = "1" if self.accidental == "sharp" else "-1"
                if self.accidental == "natural": alter = "0"
                ET.SubElement(p, "alter").text = alter
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

def get_scale_note(root, scale_intervals, index, octave_offset=0):
    root_idx = NOTES.index(root)
    deg = index % len(scale_intervals)
    oct_shift = index // len(scale_intervals)
    interval = scale_intervals[deg]
    abs_idx = (root_idx + interval)
    note_name = NOTES[abs_idx % 12]
    octave = 4 + octave_offset + (abs_idx // 12) + oct_shift
    acc = "sharp" if "#" in note_name else None
    return note_name[0], octave, acc

# --- NEW SHORTER ENGINES ---

def gen_esp(m):
    # Inspired by E.S.P.
    # Fast, Intervallic (4ths), Quartal Harmony
    # Progression: Emaj7 - F7 - Emaj7 - F7 (Shift)
    
    local_m = (m-1) % 2
    root = "E" if local_m == 0 else "F"
    
    high = []
    low = []
    
    # Bass: Walking fast
    low.append(Note(root[0], DIVISIONS, "quarter", octave=3, accidental="sharp" if "#" in root else None))
    low.append(Note(NOTES[(NOTES.index(root)+7)%12][0], DIVISIONS, "quarter", octave=3)) # 5th
    low.append(Note(NOTES[(NOTES.index(root)+2)%12][0], DIVISIONS, "quarter", octave=3)) # 2nd
    low.append(Note(NOTES[(NOTES.index(root)+11)%12][0], DIVISIONS, "quarter", octave=3)) # 7th
    
    # Melody: Perfect 4ths climbing
    # E.g. B - E - A
    base_idx = NOTES.index(root)
    n1 = NOTES[(base_idx + 11) % 12] # 7th
    n2 = NOTES[(base_idx + 4) % 12] # 3rd
    n3 = NOTES[(base_idx + 9) % 12] # 6th
    
    if m % 2 != 0:
        high.append(Note(n1[0], DIVISIONS, "quarter", octave=4, accidental="sharp" if "#" in n1 else None))
        high.append(Note(n2[0], DIVISIONS, "quarter", octave=4, accidental="sharp" if "#" in n2 else None))
        high.append(Note(n3[0], DIVISIONS*2, "half", octave=4, accidental="sharp" if "#" in n3 else None))
    else:
        # Descending 4ths
        high.append(Note(n3[0], DIVISIONS, "quarter", octave=5, accidental="sharp" if "#" in n3 else None))
        high.append(Note(n2[0], DIVISIONS, "quarter", octave=5, accidental="sharp" if "#" in n2 else None))
        high.append(Note(n1[0], DIVISIONS*2, "half", octave=4, accidental="sharp" if "#" in n1 else None))

    return high, low

def gen_infant_eyes(m):
    # Inspired by Infant Eyes
    # Ballad, 4/4, Slow harmonic rhythm
    # Progression: Bbmin7 - Eb9sus (Dark, floating)
    
    high = []
    low = []
    
    # Bass: Root - 5 pedal
    low.append(Note("A", DIVISIONS*4, "whole", octave=2, accidental="sharp")) # Bb (A#)
    
    # Melody: Sustained emotive notes (9ths, 11ths)
    # Chord Bbm7: Notes Bb, Db, F, Ab
    # Color: C (9), Eb (11)
    
    if m % 2 != 0:
        # Long 9th
        high.append(Note("C", DIVISIONS*3, "half", dot=True, octave=4))
        high.append(Note("C", DIVISIONS, "quarter", octave=4, accidental="sharp")) # Move to C# (Db)
    else:
        # Resolve to 5th
        high.append(Note("F", DIVISIONS*4, "whole", octave=4))
        
    return high, low

def gen_witch_hunt(m):
    # Inspired by Witch Hunt
    # Fanfare, Dotted Rhythms, Dark Modal
    # C minor (Aeolian)
    
    high = []
    low = []
    
    # Bass: Marcato root
    low.append(Note("C", DIVISIONS, "quarter", octave=2, articulation="accent"))
    low.append(Note(None, DIVISIONS, "quarter", is_rest=True))
    low.append(Note("G", DIVISIONS, "quarter", octave=2))
    low.append(Note(None, DIVISIONS, "quarter", is_rest=True))
    
    # Melody: Fanfare "Da-da DAAAA"
    # G - Ab - C
    if m % 2 != 0:
        high.append(Note(None, DIVISIONS, "quarter", is_rest=True))
        high.append(Note("G", DIVISIONS//2, "eighth", octave=4))
        high.append(Note("G", DIVISIONS//2, "eighth", octave=4, accidental="sharp")) # G# (Ab)
        high.append(Note("C", DIVISIONS*2, "half", octave=5, articulation="accent"))
    else:
        # Response
        high.append(Note("A", DIVISIONS*3, "half", dot=True, octave=4, accidental="sharp")) # Bb
        high.append(Note("G", DIVISIONS, "quarter", octave=4))

    return high, low

def gen_nefertiti(m):
    # Inspired by Nefertiti
    # Melodic Stasis (Horns repeat) + Rhythmic Activity (Drums/Piano fill)
    # Melody is slow and repetitive, Bass is active
    
    high = []
    low = []
    
    # Melody: Slow repeating phrase (Abmaj7 #5)
    # C - E - G#
    high.append(Note("C", DIVISIONS*2, "half", octave=5))
    high.append(Note("E", DIVISIONS, "quarter", octave=5))
    high.append(Note("G", DIVISIONS, "quarter", octave=5, accidental="sharp"))
    
    # Bass: "Solar" style interactive walking (broken)
    # Active 8ths
    low.append(Note("G", DIVISIONS//2, "eighth", octave=3, accidental="sharp"))
    low.append(Note("C", DIVISIONS//2, "eighth", octave=3))
    low.append(Note("E", DIVISIONS, "quarter", octave=3))
    low.append(Note("F", DIVISIONS, "quarter", octave=3))
    low.append(Note("B", DIVISIONS, "quarter", octave=2))
    
    return high, low

def gen_pinocchio(m):
    # Inspired by Pinocchio
    # Angular, Slinky, chromatic twists
    # Fast Swing
    
    high = []
    low = []
    
    # Bass: Fast Walk
    low.append(Note("F", DIVISIONS, "quarter", octave=2))
    low.append(Note("A", DIVISIONS, "quarter", octave=2))
    low.append(Note("C", DIVISIONS, "quarter", octave=3))
    low.append(Note("E", DIVISIONS, "quarter", octave=3))
    
    # Melody: Twisting chromatic line
    # Start high, twist down
    if m % 2 != 0:
        high.append(Note(None, DIVISIONS, "quarter", is_rest=True))
        high.append(Note("A", DIVISIONS//2, "eighth", octave=4))
        high.append(Note("G", DIVISIONS//2, "eighth", octave=4, accidental="sharp"))
        high.append(Note("G", DIVISIONS//2, "eighth", octave=4, accidental="natural"))
        high.append(Note("F", DIVISIONS//2, "eighth", octave=4, accidental="sharp"))
        high.append(Note("F", DIVISIONS, "quarter", octave=4, accidental="natural"))
    else:
        high.append(Note("E", DIVISIONS, "quarter", octave=4))
        high.append(Note("D", DIVISIONS, "quarter", octave=4, accidental="sharp")) # Eb
        high.append(Note(None, DIVISIONS*2, "half", is_rest=True))
        
    return high, low

# --- MAIN ---

def main():
    root = ET.Element("score-partwise", version="3.1")
    work = ET.SubElement(root, "work")
    ET.SubElement(work, "work-title").text = TITLE
    
    part_list = ET.SubElement(root, "part-list")
    sp = ET.SubElement(part_list, "score-part", id=REDUCTION_PART["id"])
    ET.SubElement(sp, "part-name").text = REDUCTION_PART["name"]
    
    p_node = ET.SubElement(root, "part", id=REDUCTION_PART["id"])
    
    # 5 Sections * 6 Measures = 30 Measures Total
    # Section 1: 1-6
    # Section 2: 7-12
    # Section 3: 13-18
    # Section 4: 19-24
    # Section 5: 25-30
    
    for m in range(1, 31):
        style = ""
        rehearsal = None
        
        if 1 <= m <= 6:
            style = "ESP"
            if m == 1: rehearsal = "Inspired by E.S.P."
        elif 7 <= m <= 12:
            style = "Infant Eyes"
            if m == 7: rehearsal = "Inspired by Infant Eyes"
        elif 13 <= m <= 18:
            style = "Witch Hunt"
            if m == 13: rehearsal = "Inspired by Witch Hunt"
        elif 19 <= m <= 24:
            style = "Nefertiti"
            if m == 19: rehearsal = "Inspired by Nefertiti"
        else:
            style = "Pinocchio"
            if m == 25: rehearsal = "Inspired by Pinocchio"
            
        m_node = ET.SubElement(p_node, "measure", number=str(m))
        
        # Attributes M1
        if m == 1:
            attr = ET.SubElement(m_node, "attributes")
            ET.SubElement(attr, "divisions").text = str(DIVISIONS)
            ET.SubElement(attr, "staves").text = "2"
            c1 = ET.SubElement(attr, "clef", number="1")
            ET.SubElement(c1, "sign").text = "G"
            ET.SubElement(c1, "line").text = "2"
            c2 = ET.SubElement(attr, "clef", number="2")
            ET.SubElement(c2, "sign").text = "F"
            ET.SubElement(c2, "line").text = "4"
            time = ET.SubElement(attr, "time")
            ET.SubElement(time, "beats").text = "4"
            ET.SubElement(time, "beat-type").text = "4"
            
        if rehearsal:
            d = ET.SubElement(m_node, "direction", placement="above")
            dt = ET.SubElement(d, "direction-type")
            ET.SubElement(dt, "rehearsal").text = rehearsal
            
        # Generate
        if style == "ESP": h, l = gen_esp(m)
        elif style == "Infant Eyes": h, l = gen_infant_eyes(m)
        elif style == "Witch Hunt": h, l = gen_witch_hunt(m)
        elif style == "Nefertiti": h, l = gen_nefertiti(m)
        else: h, l = gen_pinocchio(m)
        
        # Write High (Voice 1)
        for n in h:
            x = n.to_xml()
            ET.SubElement(x, "staff").text = "1"
            ET.SubElement(x, "voice").text = "1"
            m_node.append(x)
            
        dur = sum(n.duration for n in h)
        backup = ET.SubElement(m_node, "backup")
        ET.SubElement(backup, "duration").text = str(dur)
        
        # Write Low (Voice 2)
        for n in l:
            x = n.to_xml()
            ET.SubElement(x, "staff").text = "2"
            ET.SubElement(x, "voice").text = "2"
            m_node.append(x)

    tree = ET.ElementTree(root)
    ET.indent(tree, space="  ", level=0)
    tree.write(OUTPUT_FILE, encoding="UTF-8", xml_declaration=True)
    print(f"Generated {OUTPUT_FILE}")

if __name__ == "__main__":
    main()

