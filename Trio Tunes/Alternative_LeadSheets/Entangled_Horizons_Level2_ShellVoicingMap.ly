\version "2.24.0"

\header {
  title = "Entangled Horizons"
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
  e1:m
  d1:m
  c1:maj
  b1:m5-
  a1:m
  g1:maj
  fis1:m5-
  e1:m
  e1:m
  d1:m
  c1
  b1:m
  a1:m
  g1
  fis1:dim
  e1:m
}

notation = {
  \clef "treble_8"
  \key e \minor
  \time 4/4
  
  \mark \markup { \box "A" }
  <e g c'>1
  <a c' g'>1
  <g c' fis'>1
  <a cis' g'>1
  <d g d'>1
  <d g d'>1
  <b d' g'>1
  <e g c'>1
  \mark \markup { \box "B" }
  <e g c'>1
  <a c' f'>1
  <g c' e'>1
  <a c' fis'>1
  <d g c'>1
  <d g c'>1
  <b d' g'>1
  <e g c'>1
  \bar "|."
}

tabNotation = {
  \mark \markup { \box "A" }
  <e\5 g\4 c'\3>1
  <a\4 c'\3 g'\2>1
  <g\4 c'\3 fis'\2>1
  <a\4 cis'\3 g'\2>1
  <d\5 g\4 d'\3>1
  <d\5 g\4 d'\3>1
  <b\4 d'\3 g'\2>1
  <e\5 g\4 c'\3>1
  \mark \markup { \box "B" }
  <e\5 g\4 c'\3>1
  <a\4 c'\3 f'\2>1
  <g\4 c'\3 e'\2>1
  <a\4 c'\3 fis'\2>1
  <d\5 g\4 c'\3>1
  <d\5 g\4 c'\3>1
  <b\4 d'\3 g'\2>1
  <e\5 g\4 c'\3>1
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
