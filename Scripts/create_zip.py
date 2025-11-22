import zipfile
import os

files_to_zip = [
    "V3_RC_Presets_Full.json",
    "rc_liveset.json",
    "rc_transformations.json",
    "the_score_playbackmap.json",
    "the_score_playbackmap.txt",
    "small_jazz_orchestra_template.musicxml",
    "Bebop_Language_Project_V3_Master.md",
    "README.md"
]

output_zip = "Bebop_Language_Project_V3_Rebuild.zip"

def create_zip():
    with zipfile.ZipFile(output_zip, 'w') as zipf:
        for file in files_to_zip:
            if os.path.exists(file):
                zipf.write(file)
                print(f"Added {file}")
            else:
                print(f"Warning: {file} not found")
    print(f"Created {output_zip}")

if __name__ == "__main__":
    create_zip()
