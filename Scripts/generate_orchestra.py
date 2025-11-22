import xml.etree.ElementTree as ET
import copy

# Define the structure of the piece
SECTIONS = [
    {"name": "Swing", "measures": range(1, 19), "style": "swing", "time": (4, 4)},
    {"name": "Fusion", "measures": range(19, 37), "style": "fusion", "time": (7, 4)},
    {"name": "Ballad", "measures": range(37, 55), "style": "ballad", "time": (4, 4)}
]

INSTRUMENTS = [
    {"id": "P1", "name": "Alto Sax 1", "role": "melody_lead", "midi": 66},
    {"id": "P2", "name": "Alto Sax 2", "role": "harmony_high", "midi": 66},
    {"id": "P3", "name": "Tenor Sax 1", "role": "harmony_mid", "midi": 67},
    {"id": "P4", "name": "Tenor Sax 2", "role": "counter_melody", "midi": 67},
    {"id": "P5", "name": "Baritone Sax", "role": "bass_line_doubling", "midi": 68},
    {"id": "P6", "name": "Trumpet 1", "role": "punches_high", "midi": 57},
    {"id": "P7", "name": "Trombone 1", "role": "punches_low", "midi": 58},
    {"id": "P8", "name": "Jazz Guitar", "role": "comping", "midi": 27},
    {"id": "P9", "name": "Piano", "role": "comping_rhythm", "midi": 1},
    {"id": "P10", "name": "Upright Bass", "role": "bass_line", "midi": 33},
    {"id": "P11", "name": "Drum Set", "role": "drums", "midi": 119} # simplified mapping
]

def create_note(step, octave, duration, type_str, accidental=None, dot=False):
    note = ET.Element("note")
    pitch = ET.SubElement(note, "pitch")
    ET.SubElement(pitch, "step").text = step
    ET.SubElement(pitch, "octave").text = str(octave)
    if accidental:
        ET.SubElement(pitch, "alter").text = "1" if accidental == "sharp" else "-1"
        ET.SubElement(note, "accidental").text = accidental
    
    dur_val = duration
    ET.SubElement(note, "duration").text = str(dur_val)
    ET.SubElement(note, "type").text = type_str
    if dot:
        ET.SubElement(note, "dot")
    return note

def create_rest(duration, type_str):
    note = ET.Element("note")
    ET.SubElement(note, "rest")
    ET.SubElement(note, "duration").text = str(duration)
    ET.SubElement(note, "type").text = type_str
    return note

def generate_measure_content(measure_num, instrument_role):
    """Generates jazz content based on measure number (section) and role."""
    
    # Determine Section
    section = next(s for s in SECTIONS if measure_num in s["measures"])
    style = section["style"]
    
    # Setup measure element (attributes only on m1, m19, m37)
    measure = ET.Element("measure", number=str(measure_num))
    
    # Add Attributes for key/time changes
    if measure_num in [1, 19, 37]:
        attr = ET.SubElement(measure, "attributes")
        divs = ET.SubElement(attr, "divisions")
        divs.text = "2" # 1 = eighth note
        key = ET.SubElement(attr, "key")
        ET.SubElement(key, "fifths").text = "0"
        time = ET.SubElement(attr, "time")
        ET.SubElement(time, "beats").text = str(section["time"][0])
        ET.SubElement(time, "beat-type").text = str(section["time"][1])
        if measure_num == 1:
            clef = ET.SubElement(attr, "clef")
            if instrument_role in ["bass_line", "punches_low", "bass_line_doubling"]:
                ET.SubElement(clef, "sign").text = "F"
                ET.SubElement(clef, "line").text = "4"
            else:
                ET.SubElement(clef, "sign").text = "G"
                ET.SubElement(clef, "line").text = "2"

    # --- CONTENT GENERATION LOGIC ---
    
    # 1. SWING SECTION (4/4)
    if style == "swing":
        if instrument_role == "melody_lead": # Bird
            # Bebop run pattern
            measure.append(create_note("C", 5, 1, "eighth"))
            measure.append(create_note("E", 5, 1, "eighth"))
            measure.append(create_note("G", 5, 1, "eighth"))
            measure.append(create_note("A", 5, 1, "eighth"))
            measure.append(create_note("B", 5, 2, "quarter"))
            measure.append(create_rest(2, "quarter"))
        elif instrument_role == "bass_line": # Walking Bass
            measure.append(create_note("C", 3, 2, "quarter"))
            measure.append(create_note("E", 3, 2, "quarter"))
            measure.append(create_note("G", 3, 2, "quarter"))
            measure.append(create_note("A", 3, 2, "quarter"))
        elif instrument_role in ["comping", "comping_rhythm"]:
            measure.append(create_rest(2, "quarter"))
            measure.append(create_note("E", 4, 2, "quarter")) # Chord Stab
            measure.append(create_rest(4, "half"))
        else: # Horns / Backing
            measure.append(create_note("G", 4, 8, "whole")) # Pad
            
    # 2. FUSION SECTION (7/4)
    elif style == "fusion":
        if instrument_role == "melody_lead": # Scofield Lick
            measure.append(create_note("E", 5, 1, "eighth"))
            measure.append(create_note("D", 5, 1, "eighth"))
            measure.append(create_note("C", 5, 1, "eighth"))
            measure.append(create_note("B", 4, 1, "eighth"))
            measure.append(create_note("A", 4, 2, "quarter"))
            measure.append(create_note("B", 4, 2, "quarter"))
            measure.append(create_rest(6, "half", type_str="half")) # .
        elif instrument_role == "bass_line": # Ostinato
            measure.append(create_note("A", 2, 2, "quarter"))
            measure.append(create_note("C", 3, 2, "quarter"))
            measure.append(create_note("E", 3, 2, "quarter"))
            measure.append(create_note("G", 3, 2, "quarter"))
            measure.append(create_rest(6, "half"))
        elif instrument_role in ["punches_high", "punches_low"]:
            measure.append(create_rest(8, "whole")) # Space for groove
            measure.append(create_note("A", 4, 2, "quarter")) # Hit on 5
            measure.append(create_rest(4, "half"))
        else:
             measure.append(create_rest(14, "whole"))

    # 3. BALLAD SECTION (4/4)
    elif style == "ballad":
        if instrument_role == "melody_lead":
            measure.append(create_note("C", 5, 8, "whole")) # Long note
        elif instrument_role in ["harmony_high", "harmony_mid"]:
            measure.append(create_note("E", 4, 8, "whole")) # Harmony Pad
        else:
             measure.append(create_rest(8, "whole"))

    return measure

def generate_xml():
    root = ET.Element("score-partwise", version="3.1")
    
    # Work Title
    work = ET.SubElement(root, "work")
    ET.SubElement(work, "work-title").text = "Ornithology in Orbit (Full Orchestra)"
    
    # Part List
    part_list = ET.SubElement(root, "part-list")
    for instr in INSTRUMENTS:
        sp = ET.SubElement(part_list, "score-part", id=instr["id"])
        ET.SubElement(sp, "part-name").text = instr["name"]
        si = ET.SubElement(sp, "score-instrument", id=f"{instr['id']}-I1")
        ET.SubElement(si, "instrument-name").text = instr["name"]
        mi = ET.SubElement(sp, "midi-instrument", id=f"{instr['id']}-I1")
        ET.SubElement(mi, "midi-program").text = str(instr["midi"])

    # Generate Parts
    for instr in INSTRUMENTS:
        part = ET.SubElement(root, "part", id=instr["id"])
        for m in range(1, 55):
            measure_content = generate_measure_content(m, instr["role"])
            part.append(measure_content)

    # Write to file
    tree = ET.ElementTree(root)
    ET.indent(tree, space="  ", level=0)
    tree.write("Works/Ornithology_Full_Orchestra.musicxml", encoding="UTF-8", xml_declaration=True)

if __name__ == "__main__":
    generate_xml()
    print("Generation Complete.")


