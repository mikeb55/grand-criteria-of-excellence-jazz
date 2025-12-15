\version "2.24.0"

\header {
  title = "Fractured Light"
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
  fis1:m
  e1:maj
  dis1:m5-
  cis1:7
  b1:m
  a1:maj
  gis1:m5-
  fis1:m
  e1
  dis1:dim
  cis1:m
  b1:m
  a1
  gis1:dim
}

notation = {
  \clef "treble_8"
  \key fis \minor
  \time 7/4
  
  \mark \markup { \box "A" }
  <b d' fis'>1
  <e gis dis'>1
  <gis cis' fis'>1
  <gis cis' f'>1
  <a c' e'>1
  <d gis cis'>1
  <gis cis' f'>1
  \mark \markup { \box "B" }
  <b d' fis'>1
  <e gis c'>1
  <gis c' fis'>1
  <gis cis' f'>1
  <a c' fis'>1
  <d gis c'>1
  <gis cis' f'>1
  \bar "|."
}

tabNotation = {
  \mark \markup { \box "A" }
  <b\4 d'\3 fis'\2>1
  <e\5 gis\4 dis'\3>1
  <gis\4 cis'\3 fis'\2>1
  <gis\4 cis'\3 f'\2>1
  <a\4 c'\3 e'\2>1
  <d\5 gis\4 cis'\3>1
  <gis\4 cis'\3 f'\2>1
  \mark \markup { \box "B" }
  <b\4 d'\3 fis'\2>1
  <e\5 gis\4 c'\3>1
  <gis\4 c'\3 fis'\2>1
  <gis\4 cis'\3 f'\2>1
  <a\4 c'\3 fis'\2>1
  <d\5 gis\4 c'\3>1
  <gis\4 cis'\3 f'\2>1
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
