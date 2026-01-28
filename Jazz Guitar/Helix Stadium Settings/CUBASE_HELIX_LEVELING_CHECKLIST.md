# CUBASE + HELIX STADIUM — LEVELING CHECKLIST

**Purpose:** Step-by-step checklist for leveling Helix presets using Cubase SuperVision  
**Order:** Most critical items first  
**Use:** Work through sequentially during leveling sessions

---

## PRE-SETUP (CRITICAL — DO FIRST)

### 1. Helix Big Volume Knob
- [ ] **Set to FULL (unity gain)**
- [ ] **Reason:** All level control must be done within presets
- [ ] **Exception:** Only adjust if live clipping occurs (rare if presets are properly leveled)

### 2. Cubase Track Setup
- [ ] Create **mono audio track**
- [ ] Select **Helix input** as track input
- [ ] **Solo the track** (so meters read only guitar signal)
- [ ] Ensure track is **armed for recording** (if needed for monitoring)

### 3. SuperVision Plugin Setup
- [ ] Insert **SuperVision** on the mono guitar track
- [ ] Add **ONLY two meters:**
  - [ ] **True Peak (dBFS)**
  - [ ] **Loudness – Short-Term (LUFS-S)**
- [ ] Remove all other meters (clutter reduction)

### 4. Helix Looper Setup
- [ ] **Record a real musical phrase** into Helix looper
  - [ ] Include: **riff + held note**
  - [ ] Use phrase that represents typical playing dynamics
  - [ ] **Critical:** Same phrase for ALL presets (ensures identical performance)

---

## REFERENCE PRESET SETUP (CRITICAL — DO SECOND)

### 5. Select Reference Preset
- [ ] Load **reference preset** (XA / 3A / 4A)
- [ ] **Do NOT adjust levels yet** — establish baseline first

### 6. Play Reference Loop
- [ ] Play the **looped phrase** from Helix looper
- [ ] Let loop play for **at least 10-15 seconds** (for meter settling)

### 7. Record Reference Readings
- [ ] Note **True Peak (dBFS)** reading: _______________
- [ ] Note **LUFS Short-Term** reading: _______________
- [ ] **Target LUFS Range:** -17 to -19 (aim for -18)
- [ ] **If LUFS is outside target range:** Adjust Amp Channel Volume to hit -17 to -19 range
- [ ] **Re-check True Peak** after Channel Volume adjustment

### 8. Verify Non-Linear Block Behavior
- [ ] **If compressor present:** Check gain reduction meters on compressor
- [ ] Note compression amount: _______________ dB
- [ ] **If Vintage Digital Delay present:** Listen for digital clipping artifacts
- [ ] **If drive pedals present:** Verify drive character is correct

---

## LEVELING METHOD SELECTION (CRITICAL — DO THIRD)

### 9. Identify Block Types in Signal Path
- [ ] List all blocks in signal path (left to right)
- [ ] **Mark which are LINEAR:**
  - [ ] Reverb (linear — safe to adjust level before/after)
  - [ ] Cab (linear — safe to adjust level before/after)
  - [ ] EQ (linear — safe to adjust level before/after)
- [ ] **Mark which are NON-LINEAR:**
  - [ ] Compressors (NON-LINEAR — behavior changes with input level)
  - [ ] Vintage Digital Delay (NON-LINEAR — can clip with more input)
  - [ ] Drive pedals (NON-LINEAR — behavior changes with input level)

### 10. Choose Leveling Method
- [ ] **Primary method:** Use **Amp Channel Volume** (does NOT affect tone)
  - [ ] **Warning:** If leveling BEFORE compressor, compression amount will change
  - [ ] **Action required:** Re-adjust compressor Peak Reduction after leveling
- [ ] **Secondary method:** Use **Final Output block** (safest — after all non-linear blocks)
  - [ ] Use this if you want to avoid affecting compressor/delay behavior
- [ ] **DO NOT use:**
  - [ ] Master Volume (affects tone — power tube behavior)
  - [ ] Drive control (affects tone)
  - [ ] Cab Level (use only if necessary, not primary method)

---

## PRESET-BY-PRESET LEVELING (REPEAT FOR EACH PRESET)

### 11. Switch to Next Preset
- [ ] Load next preset (XB / 3B / 4B, etc.)
- [ ] **Do NOT adjust levels yet** — check baseline first

### 12. Play Same Loop
- [ ] Play the **same looped phrase** (from step 4)
- [ ] Let loop play for **at least 10-15 seconds**

### 13. Record Current Readings
- [ ] Note **True Peak (dBFS):** _______________
- [ ] Note **LUFS Short-Term:** _______________
- [ ] Calculate **dB offset vs reference:** _______________

### 14. Adjust to Target
- [ ] **Target LUFS:** -17 to -19 (aim for -18)
- [ ] **Target True Peak:** Similar range to reference (within ~2 dB)
- [ ] **Adjust using:** Amp Channel Volume (or Final Output if preferred)
- [ ] **Record new readings:**
  - [ ] True Peak: _______________
  - [ ] LUFS-S: _______________

### 15. Re-Check Non-Linear Blocks (IF LEVELING BEFORE THEM)
- [ ] **If compressor present AND you leveled before it:**
  - [ ] Check compressor gain reduction meters
  - [ ] Compare to reference compression amount
  - [ ] **Re-adjust Peak Reduction** to restore desired compression
  - [ ] Re-check LUFS-S (may have changed)
- [ ] **If Vintage Digital Delay present AND you leveled before it:**
  - [ ] Listen for digital clipping artifacts
  - [ ] Adjust delay Headroom control if needed
- [ ] **If drive pedals present AND you leveled before them:**
  - [ ] Verify drive character is still correct

### 16. Verify True Peak Range
- [ ] **True Peak should stay in similar range** to reference
- [ ] **If True Peak is too high:** Risk of clipping downstream devices
- [ ] **If True Peak is too low:** Signal-to-noise ratio may suffer
- [ ] **Action:** Fine-tune with Final Output block if needed

### 17. Document Final Settings
- [ ] Record **final Amp Channel Volume:** _______________ dB
- [ ] Record **final True Peak:** _______________ dBFS
- [ ] Record **final LUFS-S:** _______________
- [ ] Record **dB offset vs reference:** _______________

### 18. Repeat for All Presets
- [ ] Go back to **Step 11** for next preset
- [ ] Continue until all presets are leveled

---

## FINAL VERIFICATION (CRITICAL — DO LAST)

### 19. A/B Comparison Test
- [ ] Switch between reference preset and each other preset
- [ ] Play the **same looped phrase** for each
- [ ] **Listen with ears** (LUFS meter gets you in ballpark, ears make final call)
- [ ] **Check for:**
  - [ ] Smooth volume transitions (no jarring jumps)
  - [ ] Appropriate loudness progression (if intentional escalation)
  - [ ] No unexpected compression changes
  - [ ] No digital clipping artifacts

### 20. Snapshot Testing (If Using Snapshots)
- [ ] Test all snapshots within each preset
- [ ] Verify snapshot transitions are smooth
- [ ] **If snapshot levels differ:** Adjust using same method (Channel Volume or Final Output)
- [ ] **Re-check non-linear blocks** if leveling before them

### 21. Final Documentation
- [ ] Record all final Cubase SuperVision targets:
  - [ ] True Peak (dBFS) for each preset
  - [ ] LUFS Short-Term for each preset
  - [ ] dB offset vs reference for each preset
- [ ] Record all final Helix settings:
  - [ ] Amp Channel Volume for each preset
  - [ ] Final Output level (if used) for each preset

---

## TROUBLESHOOTING

### If LUFS-S is Too High (> -17)
- [ ] Reduce Amp Channel Volume
- [ ] Or reduce Final Output block level
- [ ] Re-check True Peak (should decrease proportionally)

### If LUFS-S is Too Low (< -19)
- [ ] Increase Amp Channel Volume
- [ ] Or increase Final Output block level
- [ ] Re-check True Peak (should increase proportionally)
- [ ] **Warning:** Don't exceed True Peak target range

### If True Peak is Too High (> -6 dBFS)
- [ ] Risk of clipping downstream devices
- [ ] Reduce Amp Channel Volume or Final Output
- [ ] Re-check LUFS-S (may need to accept lower LUFS for safety)

### If True Peak is Too Low (< -12 dBFS)
- [ ] Signal-to-noise ratio may suffer
- [ ] Increase Amp Channel Volume or Final Output
- [ ] Re-check LUFS-S (should increase)

### If Compressor Behavior Changed
- [ ] You leveled before the compressor
- [ ] Re-adjust Peak Reduction to restore desired compression
- [ ] Re-check LUFS-S (may have changed)

### If Digital Clipping Occurs
- [ ] You may have boosted level before Vintage Digital Delay
- [ ] Reduce level before delay, or use Final Output after delay
- [ ] Or adjust delay Headroom control

---

## QUICK REFERENCE

### Target Ranges
- **LUFS Short-Term:** -17 to -19 (aim for -18)
- **True Peak (dBFS):** Similar to reference (within ~2 dB)

### Leveling Controls (In Order of Preference)
1. **Amp Channel Volume** (primary — does NOT affect tone)
2. **Final Output block** (secondary — safest, after all non-linear blocks)
3. **DO NOT use:** Master Volume, Drive, Cab Level (for leveling)

### Linear vs Non-Linear
- **Linear:** Reverb, Cab, EQ (safe to adjust level before/after)
- **Non-Linear:** Compressors, Vintage Digital Delay, Drive pedals (behavior changes with input level)

### Critical Rules
- **Helix big volume knob:** Keep at FULL (unity gain)
- **Use looper:** Same phrase for all presets (consistent testing)
- **Re-check non-linear blocks:** If leveling before them, must re-adjust their settings
- **Use ears for final adjustments:** LUFS meter gets you in ballpark, ears make final call

---

**END OF CHECKLIST**
