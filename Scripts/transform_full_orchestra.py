import xml.etree.ElementTree as ET
import copy
import sys

# Source file path (from chat history)
SOURCE_FILE = r"c:\Users\user\OneDrive\Documents\Composition w Ilkay\Orchestral Works with Ilkay\Wonderland_V3.1.musicxml"
OUTPUT_FILE = "Works/Wonderland_Jazz_Full_Orchestra.musicxml"

# Instrument Mapping (Original -> Jazz)
INSTRUMENT_MAP = {
    "P1": {"name": "Alto Sax 1", "midi": 66}, # Flute
    "P2": {"name": "Alto Sax 2", "midi": 66}, # Oboe
    "P3": {"name": "Tenor Sax 1", "midi": 67}, # Clarinet
    "P4": {"name": "Tenor Sax 2", "midi": 67}, # Bassoon
    "P5": {"name": "Trumpet 1", "midi": 57},   # Horn 1
    "P6": {"name": "Trombone 1", "midi": 58},  # Horn 2
    "P7": {"name": "Elec Guitar", "midi": 27}, # Vln 1
    "P8": {"name": "Piano", "midi": 1},        # Vln 2 (Merged to Piano for simplicity or 2nd Gtr)
    "P9": {"name": "Piano", "midi": 1},        # Viola
    "P10": {"name": "Upright Bass", "midi": 33}, # Cello (High Bass)
    "P11": {"name": "Upright Bass", "midi": 33}  # Bass
}

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
    
    # Get measure count from first part to generate drums matching length
    measure_count = len(parts[0].findall("measure")) if parts else 0
    
    # Generate Drum Part Content
    p12 = ET.SubElement(root, "part", id="P12")
    for m in range(1, measure_count + 1):
        meas = ET.SubElement(p12, "measure", number=str(m))
        if m == 1:
            attrs = ET.SubElement(meas, "attributes")
            divs = ET.SubElement(attrs, "divisions")
            divs.text = "2"
            clef = ET.SubElement(attrs, "clef")
            ET.SubElement(clef, "sign").text = "percussion"
            
        # Simple Groove Logic based on section
        if 1 <= m <= 18: # Swing
            # Ride Cymbal Pattern on quarters
            for _ in range(4):
                n = ET.SubElement(meas, "note")
                p = ET.SubElement(n, "unpitched")
                ET.SubElement(p, "display-step").text = "G"
                ET.SubElement(p, "display-octave").text = "5"
                ET.SubElement(n, "duration").text = "2"
                ET.SubElement(n, "type").text = "quarter"
        elif 19 <= m <= 36: # Fusion 7/4
            # Kick/Snare groove
            if m == 19: # Add Time Sig
                 attrs = ET.SubElement(meas, "attributes")
                 time = ET.SubElement(attrs, "time")
                 ET.SubElement(time, "beats").text = "7"
                 ET.SubElement(time, "beat-type").text = "4"
            n = ET.SubElement(meas, "note")
            ET.SubElement(n, "rest")
            ET.SubElement(n, "duration").text = "14"
        else: # Ballad
            if m == 37:
                 attrs = ET.SubElement(meas, "attributes")
                 time = ET.SubElement(attrs, "time")
                 ET.SubElement(time, "beats").text = "4"
                 ET.SubElement(time, "beat-type").text = "4"
            n = ET.SubElement(meas, "note")
            ET.SubElement(n, "rest")
            ET.SubElement(n, "duration").text = "8"

    # 4. WRITE OUTPUT
    print(f"Writing to {OUTPUT_FILE}...")
    tree.write(OUTPUT_FILE, encoding="UTF-8", xml_declaration=True)
    print("Done.")

if __name__ == "__main__":
    main()


