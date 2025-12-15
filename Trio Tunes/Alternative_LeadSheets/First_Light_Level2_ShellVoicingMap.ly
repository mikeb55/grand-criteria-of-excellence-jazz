\version "2.24.0"

\header {
  title = "First Light"
  subtitle = "Level 2 Shell Voicing Map"
  composer = "Mike Bryant"
  tagline = ##f
}

\paper {
  #(set-paper-size "a4")
  top-margin = 12\mm
  bottom-margin = 12\mm
  left-margin = 12\mm
  right-margin = 12\mm
  indent = 0
  system-system-spacing.basic-distance = #16
  score-system-spacing.basic-distance = #14
}

chordNames = \chordmode {
  g1:maj
  g1:maj
  c1:maj
  d1:maj
  e1:m
  a1:m
  d1:maj
  g1:maj
  g1:maj
  b1:m
  d1
  g1:maj
  c1:maj
  e1:m
  a1:m
  g1:maj
}

notation = {
  \clef "treble_8"
  \key g \major
  \time 4/4
  
  \mark \markup { \box "A" }
  <d g d'>1
  <d g d'>1
  <g c' fis'>1
  <a d' f'>1
  <e g c'>1
  <d g d'>1
  <a d' f'>1
  <d g d'>1
  \mark \markup { \box "B" }
  <d g d'>1
  <a c' e'>1
  <a d' fis'>1
  <d g d'>1
  <g c' fis'>1
  <e g c'>1
  <d g d'>1
  <d g d'>1
  \bar "|."
}

tabNotation = {
  \mark \markup { \box "A" }
  <d\5 g\4 d'\3>1
  <d\5 g\4 d'\3>1
  <g\4 c'\3 fis'\2>1
  <a\4 d'\3 f'\2>1
  <e\5 g\4 c'\3>1
  <d\5 g\4 d'\3>1
  <a\4 d'\3 f'\2>1
  <d\5 g\4 d'\3>1
  \mark \markup { \box "B" }
  <d\5 g\4 d'\3>1
  <a\4 c'\3 e'\2>1
  <a\4 d'\3 fis'\2>1
  <d\5 g\4 d'\3>1
  <g\4 c'\3 fis'\2>1
  <e\5 g\4 c'\3>1
  <d\5 g\4 d'\3>1
  <d\5 g\4 d'\3>1
  \bar "|."
}

\score {
  <<
    \new ChordNames { \chordNames }
    \new Staff { \notation }
    \new TabStaff {
      \set TabStaff.stringTunings = \stringTuning <e, a, d g b e'>
      \tabNotation
    }
  >>
  \layout {
    \context {
      \Score
      \override SpacingSpanner.uniform-stretching = ##t
    }
  }
}
