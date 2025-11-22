import xml.etree.ElementTree as ET

# --- CONFIG ---
OUTPUT_FILE = "small_jazz_orchestra_template.musicxml"
TITLE = "Bebop V3 Small Jazz Orchestra Template"
DIVISIONS = 24

# Instrument Definitions per Spec
PARTS_CONFIG = [
    {"id": "P1", "name": "Flute", "midi": 73, "clef": "G"},
    {"id": "P2", "name": "Clarinet in Bb", "midi": 71, "clef": "G"},
    {"id": "P3", "name": "Flugelhorn", "midi": 56, "clef": "G"},
    {"id": "P4", "name": "Violin I", "midi": 40, "clef": "G"},
    {"id": "P5", "name": "Violin II", "midi": 40, "clef": "G"},
    {"id": "P6", "name": "Viola", "midi": 41, "clef": "C"},
    {"id": "P7", "name": "Cello", "midi": 42, "clef": "F"},
    {"id": "P8", "name": "Electric Guitar", "midi": 27, "clef": "G"},
    {"id": "P9", "name": "Piano", "midi": 0, "clef": "G"},
    {"id": "P10", "name": "Double Bass", "midi": 32, "clef": "F"},
    {"id": "P11", "name": "Light Percussion", "midi": 118, "clef": "percussion"}
]

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
            if p["id"] == "P11": # Percussion
                ET.SubElement(mi, "midi-channel").text = "10"

    def add_empty_measure(self, measure_num, part_id):
        m_node = ET.Element("measure", number=str(measure_num))
        
        if measure_num == 1:
            attr = ET.SubElement(m_node, "attributes")
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
            elif clef_def == "C":
                ET.SubElement(clef, "sign").text = "C"
                ET.SubElement(clef, "line").text = "3"
            elif clef_def == "percussion":
                ET.SubElement(clef, "sign").text = "percussion"
                ET.SubElement(clef, "line").text = "2"
            else:
                ET.SubElement(clef, "sign").text = "G"
                ET.SubElement(clef, "line").text = "2"

        # Add whole rest
        note = ET.SubElement(m_node, "note")
        ET.SubElement(note, "rest")
        ET.SubElement(note, "duration").text = str(DIVISIONS * 4)
        ET.SubElement(note, "type").text = "whole"
            
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

def main():
    gen = ScoreGenerator()
    gen.setup_score()
    
    # Create 4 empty measures
    for m in range(1, 5):
        for p in PARTS_CONFIG:
            gen.add_empty_measure(m, p["id"])

    gen.write_file()

if __name__ == "__main__":
    main()

