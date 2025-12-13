BIAB Melody SGUs - Simple Instructions

Files regenerated here
- BIAB_Melody_SGU_Builder_F11.ahk
- BIAB_Melody_SGUs_Instructions.md
- BIAB_Melody_SGUs_Instructions.pdf

Prerequisites
- Band-in-a-Box installed and working
- AutoHotkey v1.1 installed (Windows)
- Chord-only SGUs already created:
  - Orbit.SGU
  - Crystal_Silence_2.SGU
- MIDI melody files (concert pitch):
  - Orbit_Melody_CONCERT.mid
  - Crystal_Silence_2_Melody_CONCERT.mid

Folder setup
- Put ALL of the following in:
  C:\BIAB_Songs\Jazz_Trio\

  - Orbit.SGU
  - Crystal_Silence_2.SGU
  - Orbit_Melody_CONCERT.mid
  - Crystal_Silence_2_Melody_CONCERT.mid
  - BIAB_Melody_SGU_Builder_F11.ahk

How to generate Melody SGUs
1 - Open Band-in-a-Box
2 - Double-click BIAB_Melody_SGU_Builder_F11.ahk
3 - Press F11 once
4 - Wait until the confirmation message appears

Result
- Two new files will be created:
  - Orbit_Melody.SGU
  - Crystal_Silence_2_Melody.SGU

If the MIDI import does not work automatically
- BIAB menu shortcuts differ by version and language
- Do this ONE time:
  - Open Orbit.SGU manually
  - Import Orbit_Melody_CONCERT.mid into the Melody track using the menu
  - Note the exact menu path (for example: File -> Import -> MIDI Melody)
- Tell me your BIAB version and menu labels
- I will update the AHK script so it runs fully hands-free

Notes
- The melody MIDI files are in concert pitch
- Trumpet players use the Bb PDFs from the notation software
- Keep chord-only SGUs for generative use
- Use Melody SGUs for rehearsal and reference
