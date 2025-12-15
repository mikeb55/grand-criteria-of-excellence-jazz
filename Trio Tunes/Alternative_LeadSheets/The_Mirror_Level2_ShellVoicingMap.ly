\version "2.24.0"

\header {
  title = "The Mirror"
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
  aes1:maj
  f1:m
  des1:maj
  ees2:sus4 ees2:7
  aes1:maj
  bes1:m
  ges1:maj
  c2:m f2:m
  b1:maj
  e1:maj
  bes1:m
  ees1:7
  aes1:maj
  f1:m
  des2:maj des2:m
  aes1:maj
}

notation = {
  \clef "treble_8"
  \key aes \major
  \time 4/4
  
  \mark \markup { \box "A" }
  <aes c' g'>1
  <f aes ees'>1
  <g des' aes'>1
  <ees aes des'>2 <ees g des'>2
  <aes c' g'>1
  <bes des' aes'>1
  <f bes des'>1
  <ees bes c'>2 <f aes ees'>2
  \break
  \mark \markup { \box "B" }
  <dis ais dis'>1
  <e gis dis'>1
  <bes des' aes'>1
  <ees g des'>1
  \mark \markup { \box "A'" }
  <aes c' g'>1
  <f aes ees'>1
  <g des' aes'>2 <e aes des'>2
  <aes c' g'>1
  \bar "|."
}

tabNotation = {
  <aes\4 c'\3 g'\2>1
  <f\5 aes\4 ees'\3>1
  <g\4 des'\3 aes'\2>1
  <ees\5 aes\4 des'\3>2 <ees\5 g\4 des'\3>2
  <aes\4 c'\3 g'\2>1
  <bes\4 des'\3 aes'\2>1
  <f\5 bes\4 des'\3>1
  <ees\5 bes\4 c'\3>2 <f\5 aes\4 ees'\3>2
  \break
  <dis\5 ais\4 dis'\3>1
  <e\5 gis\4 dis'\3>1
  <bes\4 des'\3 aes'\2>1
  <ees\5 g\4 des'\3>1
  <aes\4 c'\3 g'\2>1
  <f\5 aes\4 ees'\3>1
  <g\4 des'\3 aes'\2>2 <e\5 aes\4 des'\3>2
  <aes\4 c'\3 g'\2>1
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
