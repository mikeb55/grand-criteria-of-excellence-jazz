# ALTERNATE HELIX PATCHES – 4A–4D

**Rig:** Line 6 Helix Stadium Floor XL  
**Signal Path:** Mono  
**FOH Access:** None (mono DI only)  
**Venue:** Boogaloo-style (jazz + rock crowd)  
**Sets:** Two 30-minute sets (jazz → fusion → rock escalation)  
**Date:** 2026-01-28

**Volume Relationship:** Bank 4 reference (4A) is -17.0 LUFS-S vs Bank 3 reference (3A) at -16.0 LUFS-S. Small intentional reset between banks. FOH-safe.

---

## PRESET 4A: MODERN JAZZ / WOOD & AIR

**Loudness Role:** Reference / Foundation  
**Narrative:** Modern Jazz / Wood & Air

### CUBASE SUPERVISION TARGETS
| Metric | Target | Notes |
|--------|--------|-------|
| True Peak (dBFS) | -9.0 | |
| LUFS Short-Term | -17.0 | Reference |
| dB Offset vs Reference | 0.0 | Reference preset |
| Amp Ch Vol | +0.0 dB | |

### SIGNAL PATH (LEFT TO RIGHT)

1. Input
2. Gate
3. Amp (US Jazz Rivet 120)
4. Cab (1x12 Jazz Rivet)
5. Reverb (Room)
6. Output

### BLOCK SETTINGS

#### 1. INPUT
- **Type:** Input
- **Input:** Guitar In
- **Gain:** 0.0 dB
- **Pan:** Center
- **Level:** 0.0 dB

#### 2. GATE
- **Type:** Gate
- **Bypass:** Off
- **Threshold:** -65 dB
- **Decay:** Slow
- **Level:** 0.0 dB

#### 3. AMP (US JAZZ RIVET 120)
- **Type:** Amp (US Jazz Rivet 120)
- **Bypass:** Off
- **Drive:** Low
- **Bass:** 5.0
- **Mid:** 5.0
- **Treble:** 5.0
- **Presence:** 5.0
- **Master:** 4.5
- **Channel Volume:** +0.0 dB
- **Level:** 0.0 dB
- **EQ:** Flat / Natural

#### 4. CAB (1X12 JAZZ RIVET)
- **Type:** Cab (1x12 Jazz Rivet)
- **Bypass:** Off
- **Mic:** 67 Condenser
- **Distance:** 2 in
- **Low Cut:** 80 Hz
- **High Cut:** 10.0 kHz
- **Level:** 0.0 dB
- **Cuts:** Minimal

#### 5. REVERB (ROOM)
- **Type:** Reverb (Room Mono)
- **Bypass:** Off
- **Decay:** 1.5 s
- **Mix:** 12%
- **Level:** 0.0 dB
- **Type:** Room Short, subtle

#### 6. OUTPUT
- **Type:** Output
- **Output:** XLR
- **Level:** 0.0 dB
- **Pan:** Center

### BLOCKS NOT PRESENT
- Drive: **NOT PRESENT**
- Feedbacker: **NOT PRESENT**
- Delay: **NOT PRESENT**
- Modulation: **NOT PRESENT**

---

## PRESET 4B: JAZZ-FUNK / GROOVE FORWARD

**Loudness Role:** Groove / Forward Motion  
**Narrative:** Jazz-Funk / Groove Forward

### CUBASE SUPERVISION TARGETS
| Metric | Target | Notes |
|--------|--------|-------|
| True Peak (dBFS) | -8.5 | |
| LUFS Short-Term | -16.2 | |
| dB Offset vs Reference | +0.4 | vs 4A |
| Amp Ch Vol | +0.4 dB | |

### SIGNAL PATH (LEFT TO RIGHT)

1. Input
2. Gate
3. Drive (Teemah!)
4. Amp (US Tweed Blues Nrm)
5. Cab (1x12 Tweed Blue)
6. Auto-Filter
7. Reverb (Plate)
8. Output

### BLOCK SETTINGS

#### 1. INPUT
- **Type:** Input
- **Input:** Guitar In
- **Gain:** 0.0 dB
- **Pan:** Center
- **Level:** 0.0 dB

#### 2. GATE
- **Type:** Gate
- **Bypass:** Off
- **Threshold:** -63 dB
- **Decay:** Medium
- **Level:** 0.0 dB

#### 3. DRIVE (TEEMAH!)
- **Type:** Drive (Teemah!)
- **Bypass:** Off
- **Gain:** 2.0
- **Tone:** 5.5
- **Level:** 4.5
- **Mix:** 100%
- **Type:** Low gain

#### 4. AMP (US TWEED BLUES NRM)
- **Type:** Amp (US Tweed Blues Nrm)
- **Bypass:** Off
- **Drive:** Edge
- **Bass:** 5.5
- **Mid:** 6.0
- **Treble:** 5.0
- **Presence:** 4.5
- **Master:** 5.0
- **Channel Volume:** +0.4 dB
- **Level:** 0.0 dB
- **EQ:** Punchy mids

#### 5. CAB (1X12 TWEED BLUE)
- **Type:** Cab (1x12 Tweed Blue)
- **Bypass:** Off
- **Mic:** 57 Dynamic
- **Distance:** 2 in
- **Low Cut:** 100 Hz
- **High Cut:** 8.5 kHz
- **Level:** 0.0 dB
- **Cuts:** Controlled lows

#### 6. AUTO-FILTER
- **Type:** Auto-Filter (Envelope)
- **Bypass:** Off
- **Filter Type:** Low Pass
- **Frequency:** 2.5 kHz
- **Resonance:** 3.0
- **Sensitivity:** 50%
- **Mix:** 30%
- **Level:** 0.0 dB
- **Type:** Envelope Subtle

#### 7. REVERB (PLATE)
- **Type:** Reverb (Plate Mono)
- **Bypass:** Off
- **Decay:** 2.0 s
- **Mix:** 18%
- **Level:** 0.0 dB
- **Type:** Plate Short

#### 8. OUTPUT
- **Type:** Output
- **Output:** XLR
- **Level:** 0.0 dB
- **Pan:** Center

### BLOCKS NOT PRESENT
- Feedbacker: **NOT PRESENT**
- Delay: **NOT PRESENT**

---

## PRESET 4C: FUSION / SUSTAIN & MOTION

**Loudness Role:** Sustain / Motion  
**Narrative:** Fusion / Sustain & Motion

### CUBASE SUPERVISION TARGETS
| Metric | Target | Notes |
|--------|--------|-------|
| True Peak (dBFS) | -7.5 | |
| LUFS Short-Term | -15.2 | |
| dB Offset vs Reference | +1.0 | vs 4A |
| Amp Ch Vol | +1.0 dB | |

### SIGNAL PATH (LEFT TO RIGHT)

1. Input
2. Gate
3. Drive (Horizon Drive)
4. Amp (Cali Texas Ch 1)
5. Cab (2x12 Cali Open)
6. Chorus
7. Delay (Analog)
8. Reverb
9. Output

### BLOCK SETTINGS

#### 1. INPUT
- **Type:** Input
- **Input:** Guitar In
- **Gain:** 0.0 dB
- **Pan:** Center
- **Level:** 0.0 dB

#### 2. GATE
- **Type:** Gate
- **Bypass:** Off
- **Threshold:** -60 dB
- **Decay:** Medium
- **Level:** 0.0 dB

#### 3. DRIVE (HORIZON DRIVE)
- **Type:** Drive (Horizon Drive)
- **Bypass:** Off
- **Gain:** 3.5
- **Tone:** 6.0
- **Level:** 5.0
- **Mix:** 100%
- **Type:** Smooth

#### 4. AMP (CALI TEXAS CH 1)
- **Type:** Amp (Cali Texas Ch 1)
- **Bypass:** Off
- **Drive:** Medium
- **Bass:** 5.0
- **Mid:** 5.5
- **Treble:** 5.5
- **Presence:** 5.0
- **Master:** 5.5
- **Channel Volume:** +1.0 dB
- **Level:** 0.0 dB
- **EQ:** Focused

#### 5. CAB (2X12 CALI OPEN)
- **Type:** Cab (2x12 Cali Open)
- **Bypass:** Off
- **Mic:** 121 Ribbon
- **Distance:** 3 in
- **Low Cut:** 90 Hz
- **High Cut:** 7.5 kHz
- **Level:** 0.0 dB
- **Cuts:** Balanced

#### 6. CHORUS
- **Type:** Chorus (Stereo)
- **Bypass:** Off
- **Rate:** 1.0 Hz
- **Depth:** 40%
- **Mix:** 20%
- **Level:** 0.0 dB
- **Type:** Stereo Light

#### 7. DELAY (ANALOG)
- **Type:** Delay (Analog Mono)
- **Bypass:** Off
- **Time:** 300 ms
- **Feedback:** 25%
- **Mix:** 18%
- **Level:** 0.0 dB
- **Type:** Analog Medium

#### 8. REVERB
- **Type:** Reverb (Plate Mono)
- **Bypass:** Off
- **Decay:** 2.5 s
- **Mix:** 20%
- **Level:** 0.0 dB

#### 9. OUTPUT
- **Type:** Output
- **Output:** XLR
- **Level:** 0.0 dB
- **Pan:** Center

### BLOCKS NOT PRESENT
- Feedbacker: **NOT PRESENT**

---

## PRESET 4D: ROCK-CREDIBLE FUSION / HEADLINER

**Loudness Role:** Headliner / Maximum Impact  
**Narrative:** Rock-Credible Fusion / Headliner

### CUBASE SUPERVISION TARGETS
| Metric | Target | Notes |
|--------|--------|-------|
| True Peak (dBFS) | -7.0 | |
| LUFS Short-Term | -14.8 | |
| dB Offset vs Reference | +1.3 | vs 4A |
| Amp Ch Vol | +1.3 dB | |

### SIGNAL PATH (LEFT TO RIGHT)

1. Input
2. Gate
3. Drive (Mid Gain)
4. Amp (Brit Plexi Brt)
5. Cab (4x12 Greenback 25)
6. Delay (Tape)
7. Reverb (Hall)
8. Output

### BLOCK SETTINGS

#### 1. INPUT
- **Type:** Input
- **Input:** Guitar In
- **Gain:** 0.0 dB
- **Pan:** Center
- **Level:** 0.0 dB

#### 2. GATE
- **Type:** Gate
- **Bypass:** Off
- **Threshold:** -58 dB
- **Decay:** Medium–Fast
- **Level:** 0.0 dB

#### 3. DRIVE (MID GAIN)
- **Type:** Drive (Mid Gain)
- **Bypass:** Off
- **Gain:** 4.5
- **Tone:** 6.5
- **Level:** 5.5
- **Mix:** 100%
- **Type:** Mid Gain

#### 4. AMP (BRIT PLEXI BRT)
- **Type:** Amp (Brit Plexi Brt)
- **Bypass:** Off
- **Drive:** Medium
- **Bass:** 5.0
- **Mid:** 6.0
- **Treble:** 5.5
- **Presence:** 5.5
- **Master:** 6.0
- **Channel Volume:** +1.3 dB
- **Level:** 0.0 dB
- **EQ:** Forward

#### 5. CAB (4X12 GREENBACK 25)
- **Type:** Cab (4x12 Greenback 25)
- **Bypass:** Off
- **Mic:** 160 Ribbon
- **Distance:** 2 in
- **Low Cut:** 100 Hz
- **High Cut:** 7.0 kHz
- **Level:** 0.0 dB
- **Cuts:** Tight

#### 6. DELAY (TAPE)
- **Type:** Delay (Tape Mono)
- **Bypass:** Off
- **Time:** 400 ms
- **Feedback:** 30%
- **Mix:** 20%
- **Level:** 0.0 dB
- **Type:** Tape Tempo

#### 7. REVERB (HALL)
- **Type:** Reverb (Hall Mono)
- **Bypass:** Off
- **Decay:** 3.5 s
- **Mix:** 25%
- **Level:** 0.0 dB
- **Type:** Hall Controlled

#### 8. OUTPUT
- **Type:** Output
- **Output:** XLR
- **Level:** 0.0 dB
- **Pan:** Center

### BLOCKS NOT PRESENT
- Feedbacker: **NOT PRESENT**
- Chorus: **NOT PRESENT**

---

## FOH APPENDIX

### SIGNAL ROUTING
- Mono line-level guitar DI
- Set console gain using Preset 4A
- Leave gain unchanged after set
- Small intentional level increases 4A → 4D
- No fader rides for solos
- Light corrective EQ only
- Avoid channel compression
- If clipping: reduce input gain or pad

### GAIN STRUCTURE
- Preset 4A: Reference level (0.0 dB offset)
- Preset 4B: +0.4 dB vs 4A
- Preset 4C: +1.0 dB vs 4A
- Preset 4D: +1.3 dB vs 4A

### BANK TRANSITION NOTES
- **Bank 3 → Bank 4:** Small intentional reset (4A is -17.0 LUFS-S vs 3A's -16.0 LUFS-S)
- Switching from 3D → 4A: Controlled step down, not a drop-out
- Switching from 3A/3B → 4A: Roughly the same or slightly quieter
- FOH does not need to touch gain when moving between banks
- Bank 3 ends hot and cinematic
- Bank 4 deliberately resets the ear for the next set, then builds again

### MONITORING
- True Peak targets vary by preset (see individual preset pages)
- LUFS Short-Term targets vary by preset (see individual preset pages)
- Use Cubase SuperVision for verification

### TROUBLESHOOTING
- If signal is too quiet: Check XLR cable, verify Helix output level
- If signal is too loud: Reduce console input gain (do not request Helix changes)
- If signal is distorted: Check console input gain staging
- If signal is missing: Verify XLR connection, check Helix power status

### NOTES
- All presets are mono
- No stereo processing
- No external effects loops
- No MIDI control available
- Preset changes are performer-controlled only
- FOH cannot access Helix unit
- Different amp/cab/effects than Presets 3A–3D
- Bank 4 uses different amp models: US Jazz Rivet 120, US Tweed Blues Nrm, Cali Texas Ch 1, Brit Plexi Brt
- Bank 4 uses different cabs: 1x12 Jazz Rivet, 1x12 Tweed Blue, 2x12 Cali Open, 4x12 Greenback 25
