
#NoEnv
SendMode Input
SetTitleMatchMode, 2
SetWorkingDir %A_ScriptDir%

; ==================================================
; BIAB Melody SGU Builder
; Hotkey: F11
; ==================================================

; -------- USER SETTINGS --------
biabWindow := "Band-in-a-Box"
songFolder := "C:\BIAB_Songs\Jazz_Trio\"
melodyFolder := "C:\BIAB_Songs\Jazz_Trio\"
outFolder := "C:\BIAB_Songs\Jazz_Trio\"
delay := 350

LoadImportSave(sguName, midiName, outName) {
  global biabWindow, songFolder, melodyFolder, outFolder, delay

  WinActivate, %biabWindow%
  Sleep, delay

  ; Open chord-only SGU
  Send, ^o
  Sleep, delay
  Send, %songFolder%%sguName%
  Sleep, delay
  Send, {Enter}
  Sleep, 900

  ; Attempt: File -> Import -> MIDI
  Send, !f
  Sleep, delay
  Send, i
  Sleep, delay
  Send, m
  Sleep, 700

  ; Select MIDI file
  Send, %melodyFolder%%midiName%
  Sleep, delay
  Send, {Enter}
  Sleep, 1000

  ; Save as new Melody SGU
  Send, ^s
  Sleep, delay
  Send, %outFolder%%outName%
  Sleep, delay
  Send, {Enter}
  Sleep, 700
}

; -------- RUN BATCH --------
F11::
  LoadImportSave("Orbit.SGU", "Orbit_Melody_CONCERT.mid", "Orbit_Melody.SGU")
  LoadImportSave("Crystal_Silence_2.SGU", "Crystal_Silence_2_Melody_CONCERT.mid", "Crystal_Silence_2_Melody.SGU")
  MsgBox, 64, BIAB Melody Factory, Done. Melody SGUs saved.
return
