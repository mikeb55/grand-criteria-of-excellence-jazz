import xml.etree.ElementTree as ET
import generate_parker_variations as v4
from generate_parker_variations import Note, ChordSymbol, DIVISIONS

# --- CONFIG ---
OUTPUT_FILE = "Works/V4_Wonderland_PianoReduction.musicxml"
TITLE = "Wonderland V4: Parker Reduction"

# Reduction Part Definition
REDUCTION_PART = {"id": "P1", "name": "Piano Reduction", "midi": 0}

# --- UTILS ---
def get_midi_pitch_from_note(note_obj):
    if note_obj.is_rest or note_obj.is_unpitched:
        return None
    
    p = note_obj.pitch
    if note_obj.accidental == "sharp" and "#" not in p: p += "#"
    elif note_obj.accidental == "flat" and "b" not in p: p += "b"
        
    flat_map = {"Bb":"A#", "Eb":"D#", "Ab":"G#", "Db":"C#", "Gb":"F#", "Cb":"B", "Fb":"E"}
    if p in flat_map: p = flat_map[p]
    
    try:
        idx = v4.NOTES.index(p)
        midi = 12 * (note_obj.octave + 1) + idx
        return midi
    except:
        return 60

def assign_staff_by_pitch(note_obj):
    """Strict Split Point at Middle C (60)."""
    midi = get_midi_pitch_from_note(note_obj)
    if midi is None: return "1" # Default rests to treble
    if midi >= 60: return "1"
    return "2"

class ReductionGenerator(v4.ScoreGenerator):
    def __init__(self):
        self.root = ET.Element("score-partwise", version="3.1")
        self.parts = {}

    def setup_score(self):
        work = ET.SubElement(self.root, "work")
        ET.SubElement(work, "work-title").text = TITLE
        part_list = ET.SubElement(self.root, "part-list")
        sp = ET.SubElement(part_list, "score-part", id=REDUCTION_PART["id"])
        ET.SubElement(sp, "part-name").text = REDUCTION_PART["name"]

def main():
    gen = ReductionGenerator()
    gen.setup_score()
    
    part_node = ET.SubElement(gen.root, "part", id=REDUCTION_PART["id"])
    
    for m in range(1, 49):
        chord = v4.get_chord_for_measure(m)
        
        # Style Selector (Same as V4)
        if 1 <= m <= 12: style = "Ornithology"
        elif 13 <= m <= 24: style = "Donna Lee"
        elif 25 <= m <= 36: style = "Scrapple"
        else: style = "Yardbird"

        m_node = ET.SubElement(part_node, "measure", number=str(m))
        
        # Attributes (M1)
        if m == 1:
            attr = ET.SubElement(m_node, "attributes")
            ET.SubElement(attr, "divisions").text = str(DIVISIONS)
            key = ET.SubElement(attr, "key")
            ET.SubElement(key, "fifths").text = "0"
            time = ET.SubElement(attr, "time")
            ET.SubElement(time, "beats").text = "4"
            ET.SubElement(time, "beat-type").text = "4"
            ET.SubElement(attr, "staves").text = "2"
            c1 = ET.SubElement(attr, "clef", number="1")
            ET.SubElement(c1, "sign").text = "G"
            ET.SubElement(c1, "line").text = "2"
            c2 = ET.SubElement(attr, "clef", number="2")
            ET.SubElement(c2, "sign").text = "F"
            ET.SubElement(c2, "line").text = "4"

        # --- COLLECT ALL NOTES ---
        # We grab the Lead (Sax) and Rhythm (Bass/Comping)
        all_notes = []
        
        # Lead Source (Part 0 - Alto Sax)
        if style == "Ornithology": 
            all_notes.extend(v4.gen_ornithology_style(0, m, chord))
        elif style == "Donna Lee": 
            all_notes.extend(v4.gen_donna_lee_style(0, m, chord))
        elif style == "Scrapple": 
            all_notes.extend(v4.gen_scrapple_style(0, m, chord))
        else: 
            all_notes.extend(v4.gen_yardbird_style(0, m, chord))

        # Bass Source (Part 5 - Bass)
        if style == "Ornithology":
             all_notes.extend(v4.gen_ornithology_style(5, m, chord))
        elif style == "Donna Lee":
             all_notes.extend(v4.gen_donna_lee_style(5, m, chord))
        elif style == "Scrapple":
             all_notes.extend(v4.gen_scrapple_style(5, m, chord))
        else:
             all_notes.extend(v4.gen_yardbird_style(5, m, chord))

        # --- SPLIT INTO STAVES ---
        staff1_notes = []
        staff2_notes = []
        
        for n in all_notes:
            s = assign_staff_by_pitch(n)
            if s == "1": staff1_notes.append(n)
            else: staff2_notes.append(n)
            
        # --- WRITE STAFF 1 (Voice 1) ---
        for n in staff1_notes:
            x = n.to_xml()
            ET.SubElement(x, "staff").text = "1"
            ET.SubElement(x, "voice").text = "1"
            m_node.append(x)
            
        # Calculate backup duration
        # Warning: If staff1 is empty, we backup 0? No, we must backup based on intended time.
        # But since we are dumping lists, we don't know the time span unless we sum durations.
        # Assume full measure (4 beats) if we are just dumping linear streams?
        # Problem: The lists are sequential in the original code (melody THEN bass).
        # We just mixed them.
        
        # FIX: We cannot mix them into one list and sort. That destroys time order.
        # We must keep the Melody Stream and Bass Stream separate.
        # But the user wants CLEF split.
        # If Melody dips low, it goes to Staff 2.
        
        # RE-STRATEGY:
        # 1. Write Melody Stream. For each note, calculate staff. 
        #    If Staff=2, we write <staff>2</staff> but KEEP <voice>1</voice>.
        #    This is cross-staff beaming in MusicXML.
        # 2. Backup.
        # 3. Write Bass Stream. For each note, calculate staff.
        #    If Staff=1, we write <staff>1</staff> but KEEP <voice>2</voice>.
        
        # -- PASS 1: MELODY (Voice 1) --
        melody_stream = []
        if style == "Ornithology": melody_stream = v4.gen_ornithology_style(0, m, chord)
        elif style == "Donna Lee": melody_stream = v4.gen_donna_lee_style(0, m, chord)
        elif style == "Scrapple": melody_stream = v4.gen_scrapple_style(0, m, chord)
        else: melody_stream = v4.gen_yardbird_style(0, m, chord)
        
        for n in melody_stream:
            x = n.to_xml()
            s = assign_staff_by_pitch(n)
            ET.SubElement(x, "staff").text = s
            ET.SubElement(x, "voice").text = "1"
            m_node.append(x)
            
        # -- BACKUP --
        dur = sum(n.duration for n in melody_stream)
        backup = ET.SubElement(m_node, "backup")
        ET.SubElement(backup, "duration").text = str(dur)
        
        # -- PASS 2: BASS (Voice 2) --
        bass_stream = []
        if style == "Ornithology": bass_stream = v4.gen_ornithology_style(5, m, chord)
        elif style == "Donna Lee": bass_stream = v4.gen_donna_lee_style(5, m, chord)
        elif style == "Scrapple": bass_stream = v4.gen_scrapple_style(5, m, chord)
        else: bass_stream = v4.gen_yardbird_style(5, m, chord)
        
        for n in bass_stream:
            x = n.to_xml()
            s = assign_staff_by_pitch(n)
            ET.SubElement(x, "staff").text = s # Cross staff if high
            ET.SubElement(x, "voice").text = "2" # Voice 2
            m_node.append(x)

    tree = ET.ElementTree(gen.root)
    ET.indent(tree, space="  ", level=0)
    tree.write(OUTPUT_FILE, encoding="UTF-8", xml_declaration=True)
    print(f"Generated {OUTPUT_FILE}")

if __name__ == "__main__":
    main()


