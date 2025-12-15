\version "2.24.0"

\header {
  title = "The Mirror 5X - Shell Voicing Map"
  composer = "Mike Bryant"
  tagline = ##f
}

\paper {
  #(set-paper-size "a4")
  top-margin = 15\mm
  bottom-margin = 15\mm
  left-margin = 15\mm
  right-margin = 15\mm
  indent = 0
}

chordNames = \chordmode {
  aes1:maj7
  f1:m7
  des1:maj7
  ees2:sus4 ees2:7
  aes1:maj7
  bes1:m7
  ges1:maj7
  c2:m7 f2:m7
  b1:maj7
  e1:maj7
  bes1:m7
  ees1:7
  aes1:maj7
  f1:m7
  des2:maj7 des2:m
  aes1:maj7
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
  <ees bes ees'>1
  <e aes ees'>1
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
  <ees\5 bes\4 ees'\3>1
  <e\5 aes\4 ees'\3>1
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
  \layout { }
}
