# Cursor.ai Cubase Template Generator Prompt

Use the following rules whenever generating Cubase templates:

## 1. Track Creation Rules
- Create Instrument Tracks for each orchestral instrument.
- Each Instrument Track must load Kontakt and the required NKI.
- Create corresponding MIDI Tracks routed to each Instrument Track.

## 2. Routing Rules
- Instrument Track audio output → Stereo Out
- MIDI Track output → assigned Instrument Track (Channel X)
- Kontakt output → st.1 routed to 1/2

## 3. Audio System Rules
- Assume FlexASIO or ASIO device with stereo output.
- Do NOT use Control Room unless specified.

## 4. Organisation Rules
- Name tracks clearly.
- Use colour-coding by section (Strings/Winds/Brass).
- Maintain score order from top to bottom.

## 5. Output Requirements
- Provide full routing table.
- Provide Kontakt instrument load list.
- Provide Cubase folder structure.
- Provide track visibility setup.
