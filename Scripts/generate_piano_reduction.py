import xml.etree.ElementTree as ET
import generate_eclectic_v3 as v3
from generate_eclectic_v3 import Note, ChordSymbol, DIVISIONS

# --- CONFIG ---
OUTPUT_FILE = "Works/V3_Wonderland_PianoReduction.musicxml"
TITLE = "Wonderland V3: Piano Reduction"

# We only need one part for the reduction: Piano Grand Staff
REDUCTION_PART = {"id": "P1", "name": "Piano Reduction", "midi": 0}

# --- UTILS ---
def get_midi_pitch_from_note(note_obj):
    # Basic parser for note object pitch string to MIDI approximation
    if note_obj.is_rest or note_obj.is_unpitched:
        return None
    
    # Pitch string format in Note object: "C", "F#", etc.
    # Octave is stored separately: note_obj.octave
    
    # Reconstruct full name for lookup
    p = note_obj.pitch
    if note_obj.accidental == "sharp" and "#" not in p:
        p += "#"
    elif note_obj.accidental == "flat" and "b" not in p:
        p += "b" # Our lookup table doesn't use flats, but let's handle normalization
        
    # Normalize flats to sharps for v3.NOTES lookup
    flat_map = {"Bb":"A#", "Eb":"D#", "Ab":"G#", "Db":"C#", "Gb":"F#", "Cb":"B", "Fb":"E"}
    if p in flat_map:
        p = flat_map[p]
    
    try:
        idx = v3.NOTES.index(p)
        midi = 12 * (note_obj.octave + 1) + idx
        return midi
    except:
        return 60 # Fallback

def assign_staff_by_pitch(note_obj):
    """
    Rule 1: > C4 (60) -> Staff 1 (Treble)
    Rule 2: < C4 (60) -> Staff 2 (Bass)
    Rule 3: C4 (60) -> Staff 1 (Default)
    """
    midi = get_midi_pitch_from_note(note_obj)
    if midi is None:
        return "1" # Default rest to treble
    
    if midi >= 60:
        return "1"
    else:
        return "2"

class ReductionGenerator(v3.ScoreGenerator):
    def __init__(self):
        self.root = ET.Element("score-partwise", version="3.1")
        self.parts = {}
        self.measure_map = {}

    def setup_score(self):
        work = ET.SubElement(self.root, "work")
        ET.SubElement(work, "work-title").text = TITLE
        
        part_list = ET.SubElement(self.root, "part-list")
        sp = ET.SubElement(part_list, "score-part", id=REDUCTION_PART["id"])
        ET.SubElement(sp, "part-name").text = REDUCTION_PART["name"]

def main():
    gen = ReductionGenerator()
    gen.setup_score()
    
    part_part = ET.SubElement(gen.root, "part", id=REDUCTION_PART["id"])
    
    # Iterate Measures
    for m in range(1, 49):
        chord = v3.get_chord_for_measure(m)
        
        # Determine Style
        if 1 <= m <= 16: style = "Monk"
        elif 17 <= m <= 32: style = "Scofield"
        else: style = "ECM"

        m_node = ET.SubElement(part_part, "measure", number=str(m))
        
        # Setup Attributes M1
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

        # --- COLLECT NOTES ---
        # We gather all notes intended for this measure.
        # Then we sort them into Staff 1 vs Staff 2 based on PITCH rules.
        # This ensures "Right Hand" vs "Left Hand" is based on register, not instrument source.
        
        notes_pool = []
        
        # Sources
        if style == "Monk":
            notes_pool.extend(v3.gen_monk_style(0, m, chord)) # Sax 1 (Lead)
            notes_pool.extend(v3.gen_monk_style(7, m, chord)) # Piano (Comp)
        elif style == "Scofield":
            notes_pool.extend(v3.gen_scofield_style(6, m, chord)) # Guitar (Lead)
            notes_pool.extend(v3.gen_scofield_style(8, m, chord)) # Bass
        else:
            notes_pool.extend(v3.gen_ecm_style(7, m, chord)) # Piano RH
            notes_pool.extend(v3.gen_ecm_style(8, m, chord)) # Bass

        # Sort into staves
        staff1_notes = []
        staff2_notes = []
        
        for n in notes_pool:
            staff_idx = assign_staff_by_pitch(n)
            if staff_idx == "1":
                staff1_notes.append(n)
            else:
                staff2_notes.append(n)
        
        # --- WRITE STAFF 1 ---
        # Warning: Mixing rhythmic streams into one staff blindly creates notation errors.
        # If Sax plays 8ths and Piano plays Quarter, XML needs voices or they conflict.
        # For this reduction, we will assume the "Lead" instrument usually dictates rhythm on top,
        # and "Bass" on bottom. 
        # If we just merged pools, we might have 6 beats in a 4 beat measure.
        # Simplified fix: We just take the Source streams again but tag them with the calculated staff.
        # Actually, the previous logic was safer for rhythm (Lead -> Top, Bass -> Bottom).
        # But the USER RULE says: "Any note > C4 to Treble".
        # This implies if the Bass plays a high fill, it should move to Treble staff.
        
        # Let's try to respect the rule by using Cross-Staff notation if possible,
        # OR just accepting that the Bass instrument *IS* the Staff 2 content, but if it goes high, we clef change?
        # No, Piano reduction usually means splitting by hand.
        
        # Let's stick to Source Separation for Rhythm Safety, but force Clef/Staff tag based on pitch?
        # No, that breaks beams.
        # Best approach for a readable XML without advanced layout engine:
        # Keep instruments separate voices, but assign them to staves based on their *average* range? 
        # Or just stick to the standard: Lead=RH, Bass=LH.
        # The User Rule is strict: "Assign ANY note...". 
        # This suggests a visual layout rule.
        
        # Let's filter the streams.
        # If a Bass note is > C4, we write it to Staff 1? That splits the bass line.
        # Correct interpretation for Piano:
        # Everything > Middle C is Right Hand.
        # Everything < Middle C is Left Hand.
        
        # To implement this strictly without breaking rhythm:
        # We process the "High Source" (Lead). If it dips below C4, it moves to Staff 2 (Cross staff).
        # We process the "Low Source" (Bass). If it goes above C4, it moves to Staff 1.
        
        # -- TREBLE SOURCE (Lead) --
        source_high = []
        if style == "Monk": source_high = v3.gen_monk_style(0, m, chord)
        elif style == "Scofield": source_high = v3.gen_scofield_style(6, m, chord)
        else: source_high = v3.gen_ecm_style(7, m, chord)
        
        for n in source_high:
            x = n.to_xml()
            # Dynamic Staff Assignment
            s = assign_staff_by_pitch(n)
            ET.SubElement(x, "staff").text = s 
            m_node.append(x)

        # -- BACKUP --
        total_dur = sum(n.duration for n in source_high)
        backup = ET.SubElement(m_node, "backup")
        ET.SubElement(backup, "duration").text = str(total_dur)
        
        # -- BASS SOURCE (Accompaniment) --
        source_low = []
        if style == "Monk": source_low = v3.gen_monk_style(7, m, chord)
        elif style == "Scofield": source_low = v3.gen_scofield_style(8, m, chord)
        else: source_low = v3.gen_ecm_style(8, m, chord)
            
        for n in source_low:
            x = n.to_xml()
            # Dynamic Staff Assignment
            s = assign_staff_by_pitch(n)
            ET.SubElement(x, "staff").text = s
            m_node.append(x)
            
    # Write
    tree = ET.ElementTree(gen.root)
    ET.indent(tree, space="  ", level=0)
    tree.write(OUTPUT_FILE, encoding="UTF-8", xml_declaration=True)
    print(f"Generated {OUTPUT_FILE}")

if __name__ == "__main__":
    main()
