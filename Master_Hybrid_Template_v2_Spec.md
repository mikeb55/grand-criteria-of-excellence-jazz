# Master Hybrid Template v2 — Cubase Spec (The Score + The Orchestra)

## Goal
Hybrid jazz/classical chamber setup with:
- The Score handling main melodic/expressive instruments.
- The Orchestra handling phrase-based string/ensemble motion.
- Scaler 3 + RapidComposer driving harmonic and motivic material.

## Instrument Assignments

### Winds / Lead
- Flute — The Score Flute (Kontakt)
- Clarinet in Bb — The Score Clarinet (Kontakt)
- Flugelhorn — The Score Flugelhorn (Kontakt)

### Strings (Phrase + Line Hybrid)
- Violin I — The Score Violin I (for lyrical lines)
- Violin II — The Orchestra High Strings Phrase instrument
- Viola — The Orchestra Viola Phrase / Mid Strings Phrase
- Cello — The Orchestra Cello Phrase / Low Strings Phrase

### Rhythm / Harmony
- Electric Guitar — Kontakt guitar or dedicated guitar VST
- Piano — Kontakt piano (or The Orchestra Keys if desired)
- Double Bass — The Score or The Orchestra Bass
- Light Percussion — The Orchestra Percussion phrase engine

## Track Structure

For each instrument:
- 1 MIDI Track (RC/Scaler source)
- 1 Instrument Track (Kontakt instance with appropriate NKI)
- Instrument Track → Stereo Out
- MIDI Track → Instrument Track

## Kontakt Instance Strategy
Option A: One Kontakt per Instrument Track  
Option B: Shared Kontakt instances per section:
- Kontakt 1: Winds (Flute, Clarinet, Flugelhorn)
- Kontakt 2: Strings (The Score + The Orchestra instruments)
- Kontakt 3: Rhythm (Bass, Percussion, Keys)

Use multi-out only if desired; otherwise keep stereo st.1 outputs.

## Folder Layout in Cubase
- Folder: 01 Winds
  - Flute MIDI
  - Flute INST
  - Clarinet MIDI
  - Clarinet INST
  - Flugelhorn MIDI
  - Flugelhorn INST

- Folder: 02 Strings
  - Violin I MIDI
  - Violin I INST (Score)
  - Violin II MIDI
  - Violin II INST (Orchestra Phrase)
  - Viola MIDI
  - Viola INST (Orchestra Phrase)
  - Cello MIDI
  - Cello INST (Orchestra Phrase)

- Folder: 03 Rhythm Section
  - Guitar MIDI + INST
  - Piano MIDI + INST
  - Bass MIDI + INST
  - Percussion MIDI + INST

- Folder: 04 Generators
  - RapidComposer
  - Scaler 3

## Ready-to-Load Requirements
- All Instrument Tracks routed to Stereo Out.
- All MIDI Tracks routed to their corresponding Instrument Tracks.
- No Bus should ever be left as "No Bus".
- Save as a Cubase Project Template once built.
