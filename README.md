# Grand Criteria of Excellence: Jazz Project

This repository houses the **Bebop-Language Project V3.0** and the **Grand Criteria of Excellence (GCE)** workflow. It integrates algorithmic composition (Python), generative AI tools (Rapid Composer), and professional scoring (Sibelius/Dorico) to create modern jazz orchestra works.

## Repository Structure

### 📂 Composition Rules
*   **Purpose:** The "Constitution" of the project.
*   **Key Files:**
    *   `GCE_Melodic_Development_Rules.md`: Core guidelines for melody and counterpoint.
    *   `composer_analysis.md`: Deep dive into Shorter, Schneider, Metheny, etc.
    *   `CLEF_ASSIGNMENT_RULES.md`: Instrumentation standards.

### 📂 Rapid Composer
*   **Purpose:** All assets for the Rapid Composer environment.
*   **Key Files:**
    *   `RC BLANK Orchestral TEMPLATE.rcCOMP`: The master template with correct 11-track routing.
    *   `Master_Composer_Prompt.md`: The AI persona prompt for guiding generation.
    *   `V3_RC_Presets_Full.json`: Custom phrase generators for Engines A-D.

### 📂 Cubase
*   **Purpose:** DAW integration.
*   **Key Files:**
    *   `Cubase_RC_TheScore_Template_Prompt.md`: Master guide for linking RC, Cubase, and Sonuscore.

### 📂 Logic
*   **Purpose:** Logic Pro X project files (Placeholders).

### 📂 Templates
*   **Purpose:** Starting points for new scores.
*   **Key Files:**
    *   `small_jazz_orchestra_template.musicxml`: Blank score with correct instrumentation.
    *   `RC_Small_Jazz_Orchestra_Template_NOTES_v2.mid`: MIDI template.

### 📂 Sonuscore Config
*   **Purpose:** Configuration for Sonuscore's "The Score".
*   **Key Files:**
    *   `the_score_playbackmap.json`: Instrument mapping definitions.

### 📂 Scripts
*   **Purpose:** Python generation tools.
*   **Key Files:**
    *   `expand_shorter_mashup_v2.py`: Advanced algorithmic composition script.
    *   `midi_writer.py`: Utility for generating RC-compatible MIDI.

### 📂 Bebop Language
*   **Purpose:** Project-specific specifications for the V3 Bebop Engine.

### 📂 Works
*   **Purpose:** The output directory for generated compositions.
*   **Key Files:** `V7_Wonderland_Orchestral_Shorter_Expanded.musicxml`, Analysis notes, and MIDI exports.

### 📂 Project Logs
*   **Purpose:** Historical record of transformations and experiments.

---

## Usage Workflow

1.  **Start:** Use `Templates/RC BLANK Orchestral TEMPLATE.rcCOMP` in Rapid Composer.
2.  **Generate:** Apply presets from `Rapid Composer/V3_RC_Presets_Full.json`.
3.  **Refine:** Use Python scripts in `Scripts/` to algorithmically expand motifs (referencing `Composition Rules`).
4.  **Export:** Output MIDI to `Works/` and import into `Templates/small_jazz_orchestra_template.musicxml`.

## Engines Overview

*   **Engine A**: Bebop (Parker, Stitt)
*   **Engine B**: Avant (Shorter, Coltrane)
*   **Engine C**: Orchestral (Maria Schneider)
*   **Engine D**: Guitar Modernism (Metheny, Scofield)
