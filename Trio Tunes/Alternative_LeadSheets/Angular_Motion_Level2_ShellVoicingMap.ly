\version "2.24.0"

\header {
  title = "Angular Motion"
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
  ges1:maj
  f1:m5-
  bes1:7
  ees1:m
  e1:dim
  aes1:m
  des1:7
  ges1:7
  ges1:maj
  aes1:m
  des1:7
  e1:m
  a1:7
  d1:maj
  d1:m
  g1:7
}

notation = {
  \clef "treble_8"
  \key ges \major
  \time 4/4
  
  \mark \markup { \box "A" }
  <fis ais cis'>1
  <f gis dis'>1
  <dis g cis'>1
  <dis gis dis'>1
  <gis c' f'>1
  <gis cis' fis'>1
  <gis cis' fis'>1
  <fis ais e'>1
  \mark \markup { \box "B" }
  <fis ais cis'>1
  <gis cis' fis'>1
  <gis cis' fis'>1
  <e g c'>1
  <d gis c'>1
  <a d' f'>1
  <a c' g'>1
  <d g cis'>1
  \bar "|."
}

tabNotation = {
  \mark \markup { \box "A" }
  <fis\5 ais\4 cis'\3>1
  <f\5 gis\4 dis'\3>1
  <dis\5 g\4 cis'\3>1
  <dis\5 gis\4 dis'\3>1
  <gis\4 c'\3 f'\2>1
  <gis\4 cis'\3 fis'\2>1
  <gis\4 cis'\3 fis'\2>1
  <fis\5 ais\4 e'\3>1
  \mark \markup { \box "B" }
  <fis\5 ais\4 cis'\3>1
  <gis\4 cis'\3 fis'\2>1
  <gis\4 cis'\3 fis'\2>1
  <e\5 g\4 c'\3>1
  <d\5 gis\4 c'\3>1
  <a\4 d'\3 f'\2>1
  <a\4 c'\3 g'\2>1
  <d\5 g\4 cis'\3>1
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
