
# Hybrid Composition Workflow (Cubase + Scaler 3 + RapidComposer + The Score + The Orchestra)
This prompt teaches Cursor.ai how to generate Cubase templates, phrase engines, and workflows using your hybrid 11‑instrument ensemble.

## 1. Ensemble Setup Rules
Your template includes:
- Flute
- Clarinet in Bb
- Flugelhorn
- Violin I
- Violin II
- Viola
- Cello
- Electric Guitar
- Piano
- Double Bass
- Light Percussion
- + Scaler 3 Instrument Track

Each instrument must exist as:
- A MIDI Track (receives MIDI from RapidComposer or Scaler)
- An Instrument Track (Kontakt hosting The Score or The Orchestra)
- Instrument Track audio routed to **Stereo Out**
- MIDI Track routed to the Instrument Track

---

## 2. Plugin Usage Logic

### A. Scaler 3 → Inspirational Engine
Use Scaler to generate:
- Modal chord progressions
- Lydian/hexatonic melodic ideas
- Polyrhythmic patterns
- Ostinati suitable for strings, winds, and guitar
- Left-hand piano pulses, right-hand arps
- Modern jazz language (enclosures, chord-scale targeting)

### B. RapidComposer → Development Engine
Use RapidComposer for:
- Intervallic cell development
- Behaviour rules (simple → complex → simple)
- Long-form melodic arcs
- Counterpoint generation
- Pattern variation
- Harmonic rhythm shaping
- Polychord structures (Tonality Vault)

### C. The Score → Melodic + Expressive Engine
Use The Score (Kontakt NKIs) for:
- Melodic lines
- Legato motifs
- Soft textures
- Cinematic arcs
- Jazz/classical hybrid phrasing

### D. The Orchestra → Phrase Engine
Use Sonuscore The Orchestra for:
- Ostinati
- Rhythmic pulses
- 3-layer motion engines
- Cinematic swells
- Quick sketching
- Layered orchestral patterns

---

## 3. Composition Workflow Rules for Cursor.ai

### Step 1 — Harmonic Planning (Scaler)
Cursor should:
- Create chord maps using modal interchange, triad pairs, or polychords
- Export chord progressions to MIDI
- Define harmonic rhythm
- Suggest Scaler performance modes

### Step 2 — Motif Creation (RapidComposer)
Cursor should:
- Use RC-like generative logic: motifs, variations, interval cells
- Generate Counterpoint voices for Violin, Clarinet, Guitar
- Use Tonality Vault triad pairs (Cmaj + Dmaj etc.)
- Create 4-note motivic cells for winds/strings

### Step 3 — Orchestration Logic
Cursor should orchestrate with these principles:
- Flugelhorn = primary melodic lead
- Violins = lyrical + rhythmic detail
- Clarinet = warm mid-voice + counterlines
- Guitar = texture, rhythmic comping, or wide-interval lines
- Piano = harmonic architecture
- Bass = root motion + modal pedal points
- Percussion = light accents

### Step 4 — Phrase Engine Integration
Cursor should:
- Trigger The Orchestra phrase layers for rhythmic support
- Trigger The Score for melodic or expressive articulations
- Apply Scaler 3 performance phrasing on top if needed

### Step 5 — Output Requirements
Cursor should produce:
- A Cubase routing table
- MIDI clips for each instrument
- Kontakt instrument list + output map
- Phrase engine assignments
- Polychord & modal explanations
- Mix suggestions

---

## 4. Composition Blueprint Generator
Cursor must be able to output full 5-minute piece blueprints using:
- Hybrid jazz/classical techniques
- Triad pairs, polychords, hexatonics
- Maria Schneider–style orchestration
- Pat Metheny–style melody arcs
- Wayne Shorter–style harmonic fluidity
- Tonality Vault rules

---

## 5. Final Cubase Template Assembly Rules
Cursor should:
1. Build MIDI + Instrument Track pairs
2. Route all Instruments → Stereo Out
3. Insert Kontakt NKIs per instrument
4. Insert Scaler 3 with performance settings
5. Add folder structure:
   - Winds
   - Brass
   - Strings
   - Guitar
   - Piano
   - Bass
   - Percussion
   - Generators (Scaler, RC)
6. Provide an ASCII block diagram of routing
7. Export Track Archive if requested

---

## End of Prompt
