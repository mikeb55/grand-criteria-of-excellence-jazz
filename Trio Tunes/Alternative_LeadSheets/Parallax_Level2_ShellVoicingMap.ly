\version "2.24.0"

\header {
  title = "Parallax"
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
  bes1:7
  bes1:7
  ees1:7
  f1:7
  bes1:7
  bes1:7
  ees1:7
  bes1:7
  bes1:7
  bes1:7
  ees1:7
  bes1:7
  g1:m
  c1:m
  f1:7
  bes1:7
}

notation = {
  \clef "treble_8"
  \key bes \major
  \time 4/4
  
  \mark \markup { \box "A" }
  <dis g cis'>1
  <dis g cis'>1
  <dis g dis'>1
  <f a dis'>1
  <dis g cis'>1
  <dis g cis'>1
  <dis g dis'>1
  <dis g cis'>1
  \mark \markup { \box "B" }
  <dis g cis'>1
  <dis g cis'>1
  <dis g dis'>1
  <dis g cis'>1
  <d g cis'>1
  <g c' f'>1
  <f a dis'>1
  <dis g cis'>1
  \bar "|."
}

tabNotation = {
  \mark \markup { \box "A" }
  <dis\5 g\4 cis'\3>1
  <dis\5 g\4 cis'\3>1
  <dis\5 g\4 dis'\3>1
  <f\5 a\4 dis'\3>1
  <dis\5 g\4 cis'\3>1
  <dis\5 g\4 cis'\3>1
  <dis\5 g\4 dis'\3>1
  <dis\5 g\4 cis'\3>1
  \mark \markup { \box "B" }
  <dis\5 g\4 cis'\3>1
  <dis\5 g\4 cis'\3>1
  <dis\5 g\4 dis'\3>1
  <dis\5 g\4 cis'\3>1
  <d\5 g\4 cis'\3>1
  <g\4 c'\3 f'\2>1
  <f\5 a\4 dis'\3>1
  <dis\5 g\4 cis'\3>1
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
