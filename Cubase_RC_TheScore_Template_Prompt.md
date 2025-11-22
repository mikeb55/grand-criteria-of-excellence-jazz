# Cursor.ai Prompt: Build a Full Cubase Template with Rapid Composer + Kontakt 8 + The Score + Ample Guitar

## Objective
Create a **fully functional Cubase project template (.cpr or Track Archive .xml)** that hosts:
- Rapid Composer VST (as MIDI generator)
- 11 single-instrument instances from **Sonuscore *The Score*** (Kontakt 8)
- 1 instance of **Ample Guitar**
- All routing from Rapid Composer → correct instrument tracks
- Correct MIDI channels per track
- Colour-coded folders, mixer groups, and labelled tracks
- Clean default gain staging
- No feedback / double-routing issues
- Full modern jazz orchestral layout suitable for Wayne Shorter / Maria Schneider style writing

---

## Instruments to Create in Cubase
### Hosted in Kontakt 8 (one instance per track):
1. Flute — The Score (Solo)
2. Clarinet in Bb — The Score (Solo)
3. Flugelhorn — The Score (use Trumpet Soft patch)
4. Violin I — The Score (Solo)
5. Violin II — The Score (Solo)
6. Viola — The Score (Solo)
7. Cello — The Score (Solo)
8. Piano — The Score Piano (or Minimalist Piano)
9. Double Bass — The Score Bass (Solo)
10. Light Percussion — The Score Soft Perc / Cymbal Textures

### External VST:
11. Electric Guitar — **Ample Guitar** (AGM/AGF/AGL/AME etc., choose the closest jazz tone)

---

## Rapid Composer Routing Requirements
### Add Rapid Composer VST as an instrument track.
Configure RC to output:

- Track 1 → MIDI Ch 1 → Flute Kontakt track
- Track 2 → MIDI Ch 2 → Clarinet Kontakt track
- Track 3 → MIDI Ch 3 → Flugelhorn Kontakt track
- Track 4 → MIDI Ch 4 → Violin I
- Track 5 → MIDI Ch 5 → Violin II
- Track 6 → MIDI Ch 6 → Viola
- Track 7 → MIDI Ch 7 → Cello
- Track 8 → MIDI Ch 8 → Electric Guitar (Ample)
- Track 9 → MIDI Ch 9 → Piano
- Track 10 → MIDI Ch 10 → Double Bass
- Track 11 → MIDI Ch 11 → Light Percussion

All Kontakt instances must receive on **MIDI channel 1 only**, but the **Cubase MIDI track feeding Kontakt must be set to the appropriate channel**, since Kontakt 8 Solo instruments ignore channel unless configured.

---

## Folder Structure
Create the following folders:

- **01 RC Engine** — Rapid Composer VST track
- **02 Winds**  
  - Flute  
  - Clarinet  
  - Flugelhorn  
- **03 Strings**  
  - Violin I  
  - Violin II  
  - Viola  
  - Cello  
- **04 Rhythm**  
  - Electric Guitar (Ample Guitar)  
  - Piano  
  - Double Bass  
  - Light Percussion  

---

## Mixer Groups (optional but ideal)
Create three group channels:

- **Winds Bus**
- **Strings Bus**
- **Rhythm Bus**

Route corresponding Kontakt outputs into their matching bus.

---

## Required Deliverables from Cursor
Cursor.ai should generate:

1. **Cubase Track Archive (.xml)**  
   - Containing all tracks, routings, folder structure, mixer groups, VST assignments.

2. **README.md**  
   - Explaining how to import the Track Archive into Cubase:  
     *Project → Import → Track Archive.*

3. **Template Notes PDF (optional)**  
   - Quick-start guide for using Rapid Composer + The Score in Cubase.

---

## Additional Specification Notes
- Ensure **no duplicate MIDI routing** (disable MIDI Thru where needed).
- Each Kontakt instance should be loaded with **exactly one Solo instrument from The Score**.
- The Guitar VST must load cleanly and be named **Electric Guitar (Ample)**.
- Colour-code tracks for clarity.
- No ensemble/multi patches — **Solo instruments only**.
- Leave tempo at default; RC will override or send MIDI clock.

---

## Final Instruction to Cursor
Generate the complete Track Archive file, verify VST plugin names match Cubase defaults, and produce a clean, ready-to-use Cubase template for this orchestral jazz setup.

