# Cursor.ai Blueprint: 5-Minute Hybrid Composition (11-Instrument Ensemble)

## Ensemble
- Flute, Clarinet in Bb, Flugelhorn
- Violin I, Violin II, Viola, Cello
- Electric Guitar, Piano, Double Bass
- Light Percussion
- Optional: Scaler 3 + RapidComposer generators

## Form (5 minutes)
- A (0:00–1:00) Dawn texture — C Lydian (Cmaj + Dmaj triad pair)
- B (1:00–2:00) First theme — Flugelhorn lead, modal jazz melody
- C (2:00–3:20) Development — polychords, rhythmic burst, string ostinati
- D (3:20–4:20) Lyrical duet — Flugelhorn + Violin I, warm strings
- E (4:20–5:00) Return & fade — C Lydian recollection, dissolving texture

## Harmonic Language
- Use C Lydian, triad pairs (Cmaj/Dmaj), hexatonics and polychords.
- Development section can use:
  - C/E, Bb/C, F#/A, Gmaj/C type polychords
  - Intervallic cells: 4ths, 6ths, and stepwise enclosures.

## Instrument Roles
- Flugelhorn: main melodic lead (Sections B & D).
- Flute: colour, high counter-melody, opening and closing textures.
- Clarinet: inner warm line, counterpoint to flugelhorn/violins.
- Violins/Viola/Cello: pads, lines, ostinati, harmonic glue.
- Electric Guitar: texture, syncopated comping, wide-interval counterlines.
- Piano: harmonic foundation, arpeggios, rhythmic support.
- Double Bass: pedal tones, root motion, modal anchors.
- Light Percussion: subtle pulses, swells, textural articulation.

## Generative Logic for Cursor
1. Use Scaler to propose a chord map and rhythmic feel per section.
2. Use RapidComposer-like logic to:
   - Generate 4–6 bar motifs for melody and counterlines.
   - Apply "simple → complex → simple" development in Sections B–D.
3. Assign phrases:
   - The Orchestra (if loaded) for ostinati in Section C.
   - The Score instruments for expressive melody lines.
4. Ensure each section:
   - Has a clear emotional centre.
   - Reuses and transforms earlier motifs.
   - Maintains coherent voice-leading and register.

## Output Expectations
- One MIDI clip per instrument, per section.
- Routing consistent with Cubase template (MIDI → Instrument → Stereo Out).
- Optional: MusicXML export aligned to the 11-part template.
