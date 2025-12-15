\version "2.24.0"

\header {
  title = "Greezy"
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
  g1:7
  c1:7
  g1:7
  g1:7
  c1:7
  cis1:dim
  g1:7
  e1:7
  a1:m
  d1:7
  g1:7
  d1:7
}

notation = {
  \clef "treble_8"
  \key g \major
  \time 4/4
  
  \mark \markup { \box "A" }
  <d g cis'>1
  <g c' e'>1
  <d g cis'>1
  <d g cis'>1
  \mark \markup { \box "B" }
  <g c' e'>1
  <gis c' f'>1
  <d g cis'>1
  <e gis cis'>1
  \mark \markup { \box "C" }
  <d g c'>1
  <a d' g'>1
  <d g cis'>1
  <a d' e'>1
  \bar "|."
}

tabNotation = {
  \mark \markup { \box "A" }
  <d\5 g\4 cis'\3>1
  <g\4 c'\3 e'\2>1
  <d\5 g\4 cis'\3>1
  <d\5 g\4 cis'\3>1
  \mark \markup { \box "B" }
  <g\4 c'\3 e'\2>1
  <gis\4 c'\3 f'\2>1
  <d\5 g\4 cis'\3>1
  <e\5 gis\4 cis'\3>1
  \mark \markup { \box "C" }
  <d\5 g\4 c'\3>1
  <a\4 d'\3 g'\2>1
  <d\5 g\4 cis'\3>1
  <a\4 d'\3 e'\2>1
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
