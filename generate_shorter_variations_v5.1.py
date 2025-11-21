import xml.etree.ElementTree as ET
import random

# --- CONFIG ---
OUTPUT_FILE = "Works/V5.1_Wonderland_PianoReduction-Wayne-Shorter.musicxml"
TITLE = "Wonderland V5.1: Shorter Variations (Enhanced)"
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
    # 0=Root, 2=Maj2, 3=Min3, 4=Maj3, 5=Perf4, 7=Perf5, etc.
    root_idx = NOTES.index(root)
    
    # Calculate scale degree
    deg = index % len(scale_intervals)
    oct_shift = index // len(scale_intervals)
    
    interval = scale_intervals[deg]
    abs_idx = (root_idx + interval)
    
    note_name = NOTES[abs_idx % 12]
    octave = 4 + octave_offset + (abs_idx // 12) + oct_shift
    
    acc = None
    if "#" in note_name: acc = "sharp"
    elif "b" in note_name: acc = "flat" # Our list doesn't have flats but logic holds
    
    return note_name[0], octave, acc

# --- SHORTER ENGINES (ENHANCED) ---

def gen_footprints(m):
    # 6/4 Minor Blues Feel
    # Bass: Ostinato C-G-Bb (Standard) but move it for blues changes
    # Changes: Cmin (4 bars) -> Fmin (2) -> Cmin (2) -> D7alt -> Db7alt -> Cmin
    
    # Progression Logic
    local_m = (m - 1) % 12 # 0-11
    if local_m < 4: root, scale = "C", "minor" # Cmin
    elif local_m < 6: root, scale = "F", "minor" # Fmin
    elif local_m < 8: root, scale = "C", "minor" # Cmin
    elif local_m == 8: root, scale = "D", "altered" # D7
    elif local_m == 9: root, scale = "C#", "altered" # Db7 (C#)
    else: root, scale = "C", "minor" # Cmin
    
    high = []
    low = []
    
    # Bass Line (Ostinato adapted to root)
    # R - 5 - b7
    # Intervals: 0, 7, 10
    r_idx = NOTES.index(root)
    for interval in [0, 7, 10]:
        idx = (r_idx + interval) % 12
        n = NOTES[idx]
        acc = "sharp" if "#" in n else None
        low.append(Note(n[0], DIVISIONS*2, "half", octave=2, accidental=acc))

    # Melody: Quartal Stabs moving up/down
    # "Question and Answer"
    if m % 2 != 0:
        # Rest
        high.append(Note(None, DIVISIONS*2, "half", is_rest=True))
        # Stab (Root + 4th + 7th)
        # Randomized inversion
        inv = random.choice([0, 1, 2])
        stab_root_idx = (r_idx + (inv * 2)) % 12 # Simple shift
        n_stab = NOTES[stab_root_idx]
        high.append(Note(n_stab[0], DIVISIONS*2, "half", octave=4, articulation="accent"))
        high.append(Note(NOTES[(stab_root_idx+5)%12][0], DIVISIONS*2, "half", octave=4))
    else:
        # Echo
        high.append(Note(None, DIVISIONS*3, "half", dot=True, is_rest=True))
        target = NOTES[(r_idx + 3) % 12] # minor 3rd
        high.append(Note(target[0], DIVISIONS*3, "half", dot=True, octave=4, articulation="tenuto"))
        
    return high, low

def gen_speak_no_evil(m):
    # Flowing Hard Bop
    # Progression: Cmaj7 - Dbmaj7 - Ebmaj7 - Bmaj7 (Non-functional parallel)
    chords = ["C", "C#", "D#", "B"]
    root = chords[(m-1) % 4]
    
    high = []
    low = []
    
    # Bass: Root - 5 - Root
    low.append(Note(root[0], DIVISIONS*2, "half", octave=2, accidental="sharp" if "#" in root else None))
    low.append(Note(NOTES[(NOTES.index(root)+7)%12][0], DIVISIONS*2, "half", octave=2))
    
    # Melody: Lyrical lines (Lydian scale)
    # Scale: 0 2 4 6 7 9 11
    intervals = [0, 2, 4, 6, 7, 9, 11]
    
    # Construct a phrase
    if m % 4 == 0: # Resolution measure
        target = get_scale_note(root, intervals, 0)
        high.append(Note(target[0], DIVISIONS*4, "whole", octave=4, accidental=target[2]))
    else:
        # Moving line: Quarter, Quarter, Half
        start_deg = random.randint(0, 6)
        n1 = get_scale_note(root, intervals, start_deg)
        n2 = get_scale_note(root, intervals, start_deg + 1)
        n3 = get_scale_note(root, intervals, start_deg + 3) # Leap
        
        high.append(Note(n1[0], DIVISIONS, "quarter", octave=4, accidental=n1[2]))
        high.append(Note(n2[0], DIVISIONS, "quarter", octave=4, accidental=n2[2]))
        high.append(Note(n3[0], DIVISIONS*2, "half", octave=4, accidental=n3[2]))
        
    return high, low

def gen_yes_or_no(m):
    # Fast Swing, Driving
    # Progression: F - Eb - Db - C (Descending)
    chords = ["F", "D#", "C#", "C"]
    root = chords[(m-1) % 4]
    
    high = []
    low = []
    
    # Bass: Walking line (randomized)
    # Root, Pass, 5th, Leading
    r_idx = NOTES.index(root)
    walk = [0, 2, 7, 11]
    for interval in walk:
        idx = (r_idx + interval) % 12
        n = NOTES[idx]
        low.append(Note(n[0], DIVISIONS, "quarter", octave=3, accidental="sharp" if "#" in n else None))

    # Melody: 8th note bebop lines
    # Use Mixolydian scale
    intervals = [0, 2, 4, 5, 7, 9, 10]
    
    # 8 eighth notes
    current_deg = random.randint(0, 7)
    for i in range(8):
        # Random walk
        move = random.choice([-1, 1, 2, -2])
        current_deg += move
        n_info = get_scale_note(root, intervals, current_deg, octave_offset=1)
        high.append(Note(n_info[0], DIVISIONS//2, "eighth", octave=n_info[1], accidental=n_info[2]))
        
    return high, low

def gen_adams_apple(m):
    # Soul Jazz / Blues
    # Key: Ab (G#) -> typical Shorter key
    root = "G#"
    blues_scale = [0, 3, 5, 6, 7, 10] # Minor Blues
    
    high = []
    low = []
    
    # Bass: Funky Riff
    # Root (dot Q) - Octave (8th) - b7 (Q) - 5 (Q)
    low.append(Note(root[0], int(DIVISIONS*1.5), "quarter", dot=True, octave=2, accidental="sharp"))
    low.append(Note(root[0], DIVISIONS//2, "eighth", octave=3, accidental="sharp"))
    low.append(Note("F", DIVISIONS, "quarter", octave=2, accidental="sharp")) # b7 (F#)
    low.append(Note("D", DIVISIONS, "quarter", octave=2, accidental="sharp")) # 5 (D#)
    
    # Melody: Call and Response
    if m % 2 != 0:
        # Call: Blues Lick
        high.append(Note(None, DIVISIONS, "quarter", is_rest=True))
        # Triplet feel? No, straight 8ths for Boogaloo
        n1 = get_scale_note(root, blues_scale, 4) # 5th
        n2 = get_scale_note(root, blues_scale, 3) # b5
        n3 = get_scale_note(root, blues_scale, 2) # 4
        high.append(Note(n1[0], DIVISIONS, "quarter", octave=4, accidental=n1[2], articulation="accent"))
        high.append(Note(n2[0], DIVISIONS//2, "eighth", octave=4, accidental=n2[2]))
        high.append(Note(n3[0], DIVISIONS//2, "eighth", octave=4, accidental=n3[2]))
        high.append(Note(n3[0], DIVISIONS, "quarter", octave=4, accidental=n3[2]))
    else:
        # Response: Chord Stab
        high.append(Note("C", DIVISIONS, "quarter", octave=4)) # 3rd of Ab7
        high.append(Note(None, DIVISIONS*3, "half", dot=True, is_rest=True))
        
    return high, low

def gen_juju(m):
    # Whole Tone / Pentatonic Pedal
    # Pedal B
    root = "B"
    
    high = []
    low = []
    
    # Bass: Drone
    low.append(Note(root[0], DIVISIONS*4, "whole", octave=2))
    
    # Melody: Short repetitive motif that shifts
    # Motif: B - D - E (1 - b3 - 4)
    motif_intervals = [0, 3, 5]
    shift = (m // 4) * 2 # Transpose up a step every 4 bars
    
    # Rhythm: Q Q H
    for i, interval in enumerate(motif_intervals):
        idx = (NOTES.index(root) + interval + shift) % 12
        n_name = NOTES[idx]
        dur = DIVISIONS if i < 2 else DIVISIONS*2
        type_s = "quarter" if i < 2 else "half"
        
        high.append(Note(n_name[0], dur, type_s, octave=4, accidental="sharp" if "#" in n_name else None))
        
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
    
    # 5 Sections of 12 bars = 60 bars
    for m in range(1, 61):
        style = ""
        rehearsal = None
        if 1 <= m <= 12:
            style = "Footprints"
            if m == 1: rehearsal = "Inspired by Footprints"
        elif 13 <= m <= 24:
            style = "Speak No Evil"
            if m == 13: rehearsal = "Inspired by Speak No Evil"
        elif 25 <= m <= 36:
            style = "Yes or No"
            if m == 25: rehearsal = "Inspired by Yes or No"
        elif 37 <= m <= 48:
            style = "Adams Apple"
            if m == 37: rehearsal = "Inspired by Adams Apple"
        else:
            style = "Juju"
            if m == 49: rehearsal = "Inspired by Juju"
            
        m_node = ET.SubElement(p_node, "measure", number=str(m))
        
        # Attributes
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
            ET.SubElement(time, "beats").text = "6"
            ET.SubElement(time, "beat-type").text = "4"
            
        if m == 13: # Back to 4/4
            attr = ET.SubElement(m_node, "attributes")
            time = ET.SubElement(attr, "time")
            ET.SubElement(time, "beats").text = "4"
            ET.SubElement(time, "beat-type").text = "4"

        if rehearsal:
            d = ET.SubElement(m_node, "direction", placement="above")
            dt = ET.SubElement(d, "direction-type")
            ET.SubElement(dt, "rehearsal").text = rehearsal
            
        # Generate
        if style == "Footprints": h, l = gen_footprints(m)
        elif style == "Speak No Evil": h, l = gen_speak_no_evil(m)
        elif style == "Yes or No": h, l = gen_yes_or_no(m)
        elif style == "Adams Apple": h, l = gen_adams_apple(m)
        else: h, l = gen_juju(m)
        
        # Write High (Voice 1)
        for n in h:
            x = n.to_xml()
            ET.SubElement(x, "staff").text = "1"
            ET.SubElement(x, "voice").text = "1"
            m_node.append(x)
            
        # Backup
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

