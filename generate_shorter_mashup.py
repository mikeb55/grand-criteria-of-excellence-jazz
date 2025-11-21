import xml.etree.ElementTree as ET
import random

# --- CONFIG ---
OUTPUT_FILE = "Works/V1.0-Shorter-Mash-up.musicxml"
TITLE = "Wonderland: Shorter Mash-up V1.0"
DIVISIONS = 24

# Orchestration from V4 (Bebop Quintet + Guitar)
PARTS_CONFIG = [
    {"id": "P1", "name": "Alto Sax", "midi": 65, "clef": "G"}, 
    {"id": "P2", "name": "Trumpet", "midi": 56, "clef": "G"},
    {"id": "P3", "name": "Tenor Sax", "midi": 66, "clef": "G"},
    {"id": "P4", "name": "Piano", "midi": 0, "clef": "G"}, 
    {"id": "P5", "name": "Guitar", "midi": 26, "clef": "G"},
    {"id": "P6", "name": "Upright Bass", "midi": 32, "clef": "F"},
    {"id": "P7", "name": "Drum Kit", "midi": 119, "clef": "percussion"}
]

NOTES = ["C", "C#", "D", "D#", "E", "F", "F#", "G", "G#", "A", "A#", "B"]

class Note:
    def __init__(self, pitch, duration, type_str, octave=4, accidental=None, dot=False, tie=None, articulation=None, is_rest=False, is_unpitched=False):
        self.pitch = pitch
        self.duration = duration
        self.type_str = type_str
        self.octave = octave
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

# --- ORCHESTRAL ENGINES ---

def gen_footprints_orch(part_idx, m):
    # 6/4 Hemiola
    notes = []
    
    # Bass/Piano LH: Ostinato
    if part_idx == 5: # Bass
        notes.append(Note("C", DIVISIONS*2, "half", octave=2))
        notes.append(Note("G", DIVISIONS*2, "half", octave=2))
        notes.append(Note("Bb", DIVISIONS*2, "half", octave=2, accidental="flat"))
    
    # Melody: Tenor + Trumpet
    elif part_idx in [1, 2]: 
        if m % 2 != 0:
            notes.append(Note(None, DIVISIONS*2, "half", is_rest=True))
            # Stab D-G
            step = "D" if part_idx==2 else "G"
            oct = 4
            notes.append(Note(step, DIVISIONS*2, "half", octave=oct, articulation="accent"))
            notes.append(Note(step, DIVISIONS*2, "half", octave=oct))
        else:
            notes.append(Note(None, DIVISIONS*6, "whole", dot=True, is_rest=True))

    # Alto: Counter line (Polyphony)
    elif part_idx == 0:
        if m % 2 == 0:
             notes.append(Note("Eb", DIVISIONS*6, "whole", dot=True, octave=5, accidental="flat"))
        else:
             notes.append(Note(None, DIVISIONS*6, "whole", dot=True, is_rest=True))

    # Drums: 6/4 Swing
    elif part_idx == 6:
        for _ in range(6):
            notes.append(Note("G", DIVISIONS, "quarter", octave=5, is_unpitched=True)) # Ride
            
    else:
        notes.append(Note(None, DIVISIONS*6, "whole", dot=True, is_rest=True))
        
    return notes

def gen_nefertiti_orch(part_idx, m):
    # Melodic Stasis (Horns), Active Rhythm
    notes = []
    
    # Horns: Unison slow melody
    if part_idx in [0, 1, 2]: 
        # C - E - G#
        step = ["C", "E", "G#"][part_idx % 3]
        oct = 4 if part_idx == 2 else 5
        acc = "sharp" if "#" in step else None
        
        notes.append(Note(step[0], DIVISIONS*2, "half", octave=oct, accidental=acc))
        notes.append(Note(step[0], DIVISIONS, "quarter", octave=oct, accidental=acc))
        notes.append(Note(step[0], DIVISIONS, "quarter", octave=oct, accidental=acc))
        
    # Bass: Broken Walking
    elif part_idx == 5:
        notes.append(Note("G", DIVISIONS//2, "eighth", octave=3, accidental="sharp"))
        notes.append(Note("C", DIVISIONS//2, "eighth", octave=3))
        notes.append(Note("E", DIVISIONS, "quarter", octave=3))
        notes.append(Note("F", DIVISIONS, "quarter", octave=3))
        notes.append(Note("B", DIVISIONS, "quarter", octave=2))
        
    # Drums: Busy
    elif part_idx == 6:
         for _ in range(4):
             notes.append(Note("C", DIVISIONS, "quarter", octave=4, is_unpitched=True, articulation="accent")) # Snare/Tom

    else:
        notes.append(Note(None, DIVISIONS*4, "whole", is_rest=True))
        
    return notes

def gen_pinocchio_orch(part_idx, m):
    # Angular Twist
    notes = []
    
    # Unison Line (Sax/Tpt)
    if part_idx in [0, 1]:
        if m % 2 != 0:
            notes.append(Note(None, DIVISIONS, "quarter", is_rest=True))
            notes.append(Note("A", DIVISIONS//2, "eighth", octave=4))
            notes.append(Note("G", DIVISIONS//2, "eighth", octave=4, accidental="sharp"))
            notes.append(Note("G", DIVISIONS//2, "eighth", octave=4, accidental="natural"))
            notes.append(Note("F", DIVISIONS//2, "eighth", octave=4, accidental="sharp"))
            notes.append(Note("F", DIVISIONS, "quarter", octave=4, accidental="natural"))
        else:
            notes.append(Note("E", DIVISIONS, "quarter", octave=4))
            notes.append(Note("D", DIVISIONS, "quarter", octave=4, accidental="sharp"))
            notes.append(Note(None, DIVISIONS*2, "half", is_rest=True))
            
    # Counter Point (Tenor)
    elif part_idx == 2:
         notes.append(Note("E", DIVISIONS*4, "whole", octave=4))
         
    # Bass: Fast Walk
    elif part_idx == 5:
        notes.append(Note("F", DIVISIONS, "quarter", octave=2))
        notes.append(Note("A", DIVISIONS, "quarter", octave=2))
        notes.append(Note("C", DIVISIONS, "quarter", octave=3))
        notes.append(Note("E", DIVISIONS, "quarter", octave=3))
        
    elif part_idx == 6:
         for _ in range(4):
             notes.append(Note("G", DIVISIONS, "quarter", octave=5, is_unpitched=True))

    else:
        notes.append(Note(None, DIVISIONS*4, "whole", is_rest=True))
        
    return notes

def gen_blend_orch(part_idx, m):
    # Mashup: Nefertiti Horns + Pinocchio Bass + Speak No Evil Piano
    notes = []
    
    # Horns (Nefertiti Stasis)
    if part_idx in [0, 1, 2]:
        return gen_nefertiti_orch(part_idx, m)
        
    # Bass (Pinocchio Walk)
    elif part_idx == 5:
        return gen_pinocchio_orch(part_idx, m)
        
    # Piano (Speak No Evil Lyrical Chords)
    elif part_idx == 3:
        notes.append(Note("E", DIVISIONS*3, "half", dot=True, octave=4))
        notes.append(Note("B", DIVISIONS, "quarter", octave=4))
        return notes
        
    # Drums (Busy)
    elif part_idx == 6:
         return gen_nefertiti_orch(part_idx, m)
         
    else:
         notes.append(Note(None, DIVISIONS*4, "whole", is_rest=True))
         return notes

# --- MAIN ---

def main():
    root = ET.Element("score-partwise", version="3.1")
    work = ET.SubElement(root, "work")
    ET.SubElement(work, "work-title").text = TITLE
    
    part_list = ET.SubElement(root, "part-list")
    for p in PARTS_CONFIG:
        sp = ET.SubElement(part_list, "score-part", id=p["id"])
        ET.SubElement(sp, "part-name").text = p["name"]
        mi = ET.SubElement(sp, "midi-instrument", id=f"{p['id']}-I1")
        ET.SubElement(mi, "midi-program").text = str(p["midi"])
        if p["id"] == "P7": 
             ET.SubElement(mi, "midi-channel").text = "10"
    
    # Parts container
    score_parts = {p["id"]: [] for p in PARTS_CONFIG}
    
    # 48 Measures max
    # 1-12: Footprints (6/4)
    # 13-24: Nefertiti (4/4)
    # 25-36: Pinocchio (4/4)
    # 37-48: Mashup (4/4)
    
    for m in range(1, 49):
        style = ""
        rehearsal = None
        
        if 1 <= m <= 12:
            style = "Footprints"
            if m == 1: rehearsal = "Theme A: Footprints (Hemiola)"
        elif 13 <= m <= 24:
            style = "Nefertiti"
            if m == 13: rehearsal = "Theme B: Nefertiti (Stasis)"
        elif 25 <= m <= 36:
            style = "Pinocchio"
            if m == 25: rehearsal = "Theme C: Pinocchio (Twist)"
        else:
            style = "Mashup"
            if m == 37: rehearsal = "Mashup: Nefertiti + Pinocchio + Speak No Evil"
            
        for i, p_conf in enumerate(PARTS_CONFIG):
            m_node = ET.Element("measure", number=str(m))
            
            # Attributes
            if m == 1:
                attr = ET.SubElement(m_node, "attributes")
                ET.SubElement(attr, "divisions").text = str(DIVISIONS)
                key = ET.SubElement(attr, "key")
                ET.SubElement(key, "fifths").text = "0"
                
                clef = ET.SubElement(attr, "clef")
                if p_conf["clef"] == "F":
                    ET.SubElement(clef, "sign").text = "F"
                    ET.SubElement(clef, "line").text = "4"
                elif p_conf["clef"] == "percussion":
                    ET.SubElement(clef, "sign").text = "percussion"
                    ET.SubElement(clef, "line").text = "2"
                else:
                    ET.SubElement(clef, "sign").text = "G"
                    ET.SubElement(clef, "line").text = "2"
                    
                time = ET.SubElement(attr, "time")
                ET.SubElement(time, "beats").text = "6"
                ET.SubElement(time, "beat-type").text = "4"
                
            if m == 13: # Switch to 4/4
                attr = ET.SubElement(m_node, "attributes")
                time = ET.SubElement(attr, "time")
                ET.SubElement(time, "beats").text = "4"
                ET.SubElement(time, "beat-type").text = "4"

            # Rehearsal (Lead only)
            if i == 0 and rehearsal:
                d = ET.SubElement(m_node, "direction", placement="above")
                dt = ET.SubElement(d, "direction-type")
                ET.SubElement(dt, "rehearsal").text = rehearsal
                
            # Gen Notes
            notes = []
            if style == "Footprints":
                notes = gen_footprints_orch(i, m)
            elif style == "Nefertiti":
                notes = gen_nefertiti_orch(i, m)
            elif style == "Pinocchio":
                notes = gen_pinocchio_orch(i, m)
            else:
                notes = gen_blend_orch(i, m)
                
            for n in notes:
                m_node.append(n.to_xml())
                
            score_parts[p_conf["id"]].append(m_node)
            
    # Compile
    for p_conf in PARTS_CONFIG:
        pid = p_conf["id"]
        p_node = ET.SubElement(root, "part", id=pid)
        for m in score_parts[pid]:
            p_node.append(m)
            
    tree = ET.ElementTree(root)
    ET.indent(tree, space="  ", level=0)
    tree.write(OUTPUT_FILE, encoding="UTF-8", xml_declaration=True)
    print(f"Generated {OUTPUT_FILE}")

if __name__ == "__main__":
    main()

