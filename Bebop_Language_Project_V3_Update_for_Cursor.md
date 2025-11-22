# Bebop-Language Project V3.0 — Master Update (Cursor.ai Version)

This .md file updates the **Bebop-Language Project** to **Version 3.0** for use in Cursor.ai.  
It integrates all research, composers, harmonic systems, and generative behaviours into a single clear specification Cursor can rebuild.

---

# 1. PURPOSE

Rebuild or update the **Bebop-Language Project V3.0** inside Rapid Composer, Sibelius, and Sonuscore *The Score*, using the full modern jazz language derived from:

- Parker, Sonny Stitt, Coleman Hawkins  
- Django Reinhardt, Wes Montgomery  
- Barry Harris, Sheryl Bailey, Pat Martino  
- Coltrane, Shorter, Ornette, McCoy Tyner  
- Chick Corea, Herbie Hancock  
- Metheny, Scofield, Rosenwinkel, Coryell, Abercrombie  
- Maria Schneider orchestral jazz  
- Triad-pair, hexatonic, polychord, and polyrhythmic concepts  

This version unifies bebop, post-bop, modern jazz, avant-garde, orchestral jazz, and guitar-centric language.

---

# 2. THE FOUR ENGINE ARCHITECTURE (Rapid Composer Live Mode)

Rebuild the following engines as Live Mode modules:

## Engine A — **Bebop Engine (Parker / Stitt / Barry Harris / Bailey / Martino / Django / Hawkins / Wes)**
- Target-tone gravity (3rd / 5th / 7th / 9th)  
- Bebop scales (major, dominant, 6th–diminished)  
- Approach tones + all enclosure types (SB + Django)  
- Minor-conversion logic (Martino)  
- Vertical arpeggio lines (Hawkins)  
- Octave phases + chord blocks (Wes)  
- Swing rhythm cells + anticipations  
- Default behaviour: *up-scale, down-chord* (Barry Harris)  

## Engine B — **Shorter / Coltrane / Avant Engine**
- Intervallic cells (2nds, 4ths, 5ths)  
- Sheets-of-sound (Coltrane 1-2-3-5 cells)  
- Pentatonics + hexatonics + triad superimposition  
- Altered, Whole Tone, Acoustic, Diminished  
- Side-slipping (Herbie) and cycle movement  
- Optional **harmolodic mode** (Ornette)  
- Rhythms: 3+3+2, 5+3, over-the-barline phrasing  

## Engine C — **Maria Schneider Orchestral Jazz Engine**
- Lydian / Lydian♭7 modal colour  
- String arcs, woodwind dovetailing  
- Planed clusters, pastel triad pairs  
- Polyrhythmic overlays (3 over 2, 5 over 4)  
- Chamber-jazz orchestration behaviour  
- Colour-based voice leading  

## Engine D — **Guitar Modernism Engine (Metheny / Scofield / Rosenwinkel / Abercrombie / Coryell / Martino)**
- Melodic pentatonics + wide intervals (Metheny)  
- Chromatic displacement + rhythmic attitude (Scofield)  
- Multi-octave lines + triad superimposition (Rosenwinkel)  
- Fusion/ECM linear ideas (Coryell, Abercrombie)  
- Minor-conversion + dim/aug symmetry (Martino)  
- Blues + Japanese pentatonics + modal fragments  
- 5-note ostinato patterns  

---

# 3. GLOBAL TRANSFORMATIONS (RC Live Mode)

## F2 — **Polychord Generator**
- Upper/lower triad-pair structures  
- Minor + Diminished (Martino)  
- Major + Major (Lydian)  
- Major + Minor (Dorian Hex)  
- Major + Augmented (Altered Hex)  

## F3 — **Polyrhythm Engine**
- 3-over-2  
- 5-over-4  
- 2-over-3-over-4  
- Shared triad-pair pitch pool  
- Optional symmetrical clusters (diminished/augmented)  

---

# 4. ENSEMBLE (for Sibelius + The Score)

Create an 11-instrument small jazz orchestra:

1. Flute  
2. Clarinet in Bb  
3. Flugelhorn  
4. Violin I  
5. Violin II  
6. Viola  
7. Cello  
8. Electric Guitar  
9. Piano  
10. Double Bass  
11. Light Percussion  

All instruments must map to **Sonuscore *The Score* solo patches** with working keyswitches.

---

# 5. FILES CURSOR.AI MUST GENERATE

1. **V3_RC_Presets_Full.json**  
2. **rc_liveset.json** – full engine behaviours  
3. **rc_transformations.json** – polychord + polyrhythm behaviours  
4. **the_score_playbackmap.json**  
5. **the_score_playbackmap.txt**  
6. **Bebop_Language_Project_V3_Master.pdf** (expandable)  
7. **small_jazz_orchestra_template.musicxml**  
8. **README.md** explaining RC → The Score → Sibelius workflow  
9. **Complete ZIP bundle** named:  
   **Bebop_Language_Project_V3_Rebuild.zip**

---

# 6. REQUIREMENTS

- All JSON must be valid.  
- All MusicXML must be valid and Sibelius-friendly.  
- Playback map must match *The Score* articulation structure.  
- Engines must be notation-safe (no CC clutter).  
- No Dorico output.  
- Must faithfully preserve composer behaviour rules.  

---

# 7. REBUILD INSTRUCTIONS

Using this specification, rebuild or update:

- All four generative engines  
- All phrase behaviours  
- All harmonic rules  
- All rhythmic structures  
- All scale/triad-pair/polychord pools  
- All orchestration behaviours  
- All export workflows  

Produce the full **Bebop-Language Project V3.0** environment for Rapid Composer, The Score, and Sibelius.

