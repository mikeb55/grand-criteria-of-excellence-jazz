import xml.etree.ElementTree as ET
import copy
import sys

# Source file path (from chat history)
SOURCE_FILE = r"c:\Users\user\OneDrive\Documents\Composition w Ilkay\Orchestral Works with Ilkay\Wonderland_V3.1.musicxml"
OUTPUT_FILE = "Works/Wonderland_Eclectic_Jazz.musicxml"

# Instrument Mapping (Original -> Jazz) - Keeping versatile for the mix
INSTRUMENT_MAP = {
    "P1": {"name": "Alto Sax 1", "midi": 66}, # Flute -> Sax
    "P2": {"name": "Alto Sax 2", "midi": 66}, # Oboe -> Sax
    "P3": {"name": "Tenor Sax 1", "midi": 67}, # Clarinet -> Sax
    "P4": {"name": "Tenor Sax 2", "midi": 67}, # Bassoon -> Sax
    "P5": {"name": "Trumpet 1", "midi": 57},   # Horn 1
    "P6": {"name": "Trombone 1", "midi": 58},  # Horn 2
    "P7": {"name": "Elec Guitar", "midi": 27}, # Vln 1
    "P8": {"name": "Piano", "midi": 1},        # Vln 2 (Merged to Piano for simplicity or 2nd Gtr)
    "P9": {"name": "Piano", "midi": 1},        # Viola
    "P10": {"name": "Upright Bass", "midi": 33}, # Cello (High Bass)
    "P11": {"name": "Upright Bass", "midi": 33}  # Bass
}

# Define Sections and Styles
# Total 54 Measures. 
# Let's divide them roughly:
# m1-9:   Style 2 (Gil Evans / Cool)
# m10-18: Pure Charlie Parker (Bebop)
# m19-27: Style 3 (Afro-Cuban / Latin)
# m28-36: Pure Monk (Angular / Dissonant)
# m37-45: Style 4 (ECM / Nordic)
# m46-54: Finale (Mix / Latin reprise)
SECTIONS = [
    {"range": range(1, 10), "style": "Gil Evans (Cool Jazz)", "rehearsal": "A - Cool"},
    {"range": range(10, 19), "style": "Charlie Parker (Bebop)", "rehearsal": "B - Bird"},
    {"range": range(19, 28), "style": "Afro-Cuban", "rehearsal": "C - Latin"},
    {"range": range(28, 37), "style": "Thelonious Monk", "rehearsal": "D - Monk"},
    {"range": range(37, 46), "style": "ECM Nordic", "rehearsal": "E - ECM"},
    {"range": range(46, 55), "style": "Finale", "rehearsal": "F - Outro"}
]

def main():
    print(f"Reading {SOURCE_FILE}...")
    try:
        tree = ET.parse(SOURCE_FILE)
        root = tree.getroot()
    except Exception as e:
        print(f"Error reading file: {e}")
        # Create dummy file for logic test if source missing in this env
        return

    # 1. UPDATE PART DEFINITIONS
    part_list = root.find("part-list")
    for score_part in part_list.findall("score-part"):
        pid = score_part.get("id")
        if pid in INSTRUMENT_MAP:
            new_info = INSTRUMENT_MAP[pid]
            
            # Update Name
            pn = score_part.find("part-name")
            if pn is not None:
                pn.text = new_info["name"]
            
            # Update Instrument Name
            si = score_part.find("score-instrument")
            if si is not None:
                in_name = si.find("instrument-name")
                if in_name is not None:
                    in_name.text = new_info["name"]
            
            # Update MIDI
            mi = score_part.find("midi-instrument")
            if mi is not None:
                mp = mi.find("midi-program")
                if mp is not None:
                    mp.text = str(new_info["midi"])

    # 2. ADD DRUM PART DEFINITION
    drum_part = ET.SubElement(part_list, "score-part", id="P12")
    ET.SubElement(drum_part, "part-name").text = "Drum Set"
    dsi = ET.SubElement(drum_part, "score-instrument", id="P12-I1")
    ET.SubElement(dsi, "instrument-name").text = "Drum Set"
    dmi = ET.SubElement(drum_part, "midi-instrument", id="P12-I1")
    ET.SubElement(dmi, "midi-channel").text = "10"
    ET.SubElement(dmi, "midi-program").text = "1"

    # 3. TRANSFORM CONTENT
    parts = root.findall("part")
    
    # Need to inject Rehearsal Marks into Part 1 (Lead)
    lead_part = parts[0] if parts else None
    
    # Also Generate Drum Part Content
    # Get measure count from first part to generate drums matching length
    measure_count = len(parts[0].findall("measure")) if parts else 0
    
    p12 = ET.SubElement(root, "part", id="P12")
    
    # LOOP THROUGH MEASURES FOR DRUMS & ANNOTATIONS
    for m in range(1, measure_count + 1):
        
        # Determine current style
        current_section = next((s for s in SECTIONS if m in s["range"]), None)
        style_name = current_section["style"] if current_section else "Standard"
        rehearsal_mark = current_section["rehearsal"] if current_section and m == current_section["range"].start else None

        # -- DRUMS GENERATION --
        meas = ET.SubElement(p12, "measure", number=str(m))
        if m == 1:
            attrs = ET.SubElement(meas, "attributes")
            divs = ET.SubElement(attrs, "divisions")
            divs.text = "2"
            clef = ET.SubElement(attrs, "clef")
            ET.SubElement(clef, "sign").text = "percussion"
            
        # Logic per style
        if "Gil Evans" in style_name:
            # Brushes / Soft
            n = ET.SubElement(meas, "note")
            ET.SubElement(n, "rest")
            ET.SubElement(n, "duration").text = "8" # Whole rest (assuming 4/4 base for simplicity in snippet)
            
        elif "Charlie Parker" in style_name:
            # Fast Swing Ride
            for _ in range(4):
                n = ET.SubElement(meas, "note")
                p = ET.SubElement(n, "unpitched")
                ET.SubElement(p, "display-step").text = "G" # Ride
                ET.SubElement(p, "display-octave").text = "5"
                ET.SubElement(n, "duration").text = "2"
                ET.SubElement(n, "type").text = "quarter"
                
        elif "Afro-Cuban" in style_name:
            # Clave / Timbale hits
            if m % 2 == 1: # 2-3 Clave simulation
                n = ET.SubElement(meas, "note")
                p = ET.SubElement(n, "unpitched")
                ET.SubElement(p, "display-step").text = "E" # Woodblock/Clave
                ET.SubElement(p, "display-octave").text = "5"
                ET.SubElement(n, "duration").text = "2"
                ET.SubElement(n, "type").text = "quarter"
                # ... simplified ...
            else:
                 n = ET.SubElement(meas, "note")
                 ET.SubElement(n, "rest")
                 ET.SubElement(n, "duration").text = "8"

        elif "Thelonious Monk" in style_name:
            # Disjointed Kicks
            if m % 2 == 0:
                n = ET.SubElement(meas, "note")
                p = ET.SubElement(n, "unpitched")
                ET.SubElement(p, "display-step").text = "C" # Kick
                ET.SubElement(p, "display-octave").text = "4"
                ET.SubElement(n, "duration").text = "2"
                ET.SubElement(n, "type").text = "quarter"
                ET.SubElement(n, "accidental").text = "natural"
                # rest of measure
                n = ET.SubElement(meas, "note")
                ET.SubElement(n, "rest")
                ET.SubElement(n, "duration").text = "6"
            else:
                 n = ET.SubElement(meas, "note")
                 ET.SubElement(n, "rest")
                 ET.SubElement(n, "duration").text = "8"

        elif "ECM" in style_name:
            # Washes / Cymbals only
            n = ET.SubElement(meas, "note")
            p = ET.SubElement(n, "unpitched")
            ET.SubElement(p, "display-step").text = "A" # Crash/Cymbal
            ET.SubElement(p, "display-octave").text = "5"
            ET.SubElement(n, "duration").text = "8"
            ET.SubElement(n, "type").text = "whole"
            ET.SubElement(n, "notehead").text = "diamond"
            
        else:
             n = ET.SubElement(meas, "note")
             ET.SubElement(n, "rest")
             ET.SubElement(n, "duration").text = "8"

        # -- ADD REHEARSAL MARKS TO PART 1 --
        if rehearsal_mark and lead_part is not None:
            # Find measure in lead part
            lead_meas = lead_part.find(f"./measure[@number='{m}']")
            if lead_meas is not None:
                direction = ET.SubElement(lead_meas, "direction", placement="above")
                dt = ET.SubElement(direction, "direction-type")
                # Add Rehearsal Box
                reh = ET.SubElement(dt, "rehearsal")
                reh.text = rehearsal_mark
                # Add Words for Style Description
                dt2 = ET.SubElement(direction, "direction-type")
                words = ET.SubElement(dt2, "words")
                words.text = style_name

    # 4. WRITE OUTPUT
    print(f"Writing to {OUTPUT_FILE}...")
    tree.write(OUTPUT_FILE, encoding="UTF-8", xml_declaration=True)
    print("Done.")

if __name__ == "__main__":
    main()


