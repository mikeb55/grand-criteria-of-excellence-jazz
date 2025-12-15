\version "2.24.0"

\header {
  title = "Orbit - Shell Voicing Map"
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
  f1:maj7
  ees1:maj7
  des1:maj7
  b1:maj7
  bes1:m7
  aes1:maj7
  ges1:maj7
  e1:maj7
  f1:maj7
  des1:maj7
  a1:maj7
  g1:maj7
  f1:maj7
  ees1:m7
  des1:maj7
  f1:maj7
}

notation = {
  \clef "treble_8"
  \key f \major
  \time 3/4
  
  \mark \markup { \box "A" }
  <f a e'>1
  <ees g d'>1
  <g des' aes'>1
  <ees bes ees'>1
  <bes des' aes'>1
  <aes c' g'>1
  <f bes des'>1
  <e aes ees'>1
  \break
  \mark \markup { \box "B" }
  <f a e'>1
  <g des' aes'>1
  <d aes des'>1
  <d b d'>1
  \mark \markup { \box "A'" }
  <f a e'>1
  <ees aes des'>1
  <g des' aes'>1
  <f a e'>1
  \bar "|."
}

tabNotation = {
  <f\5 a\4 e'\3>1
  <ees\5 g\4 d'\3>1
  <g\4 des'\3 aes'\2>1
  <ees\5 bes\4 ees'\3>1
  <bes\4 des'\3 aes'\2>1
  <aes\4 c'\3 g'\2>1
  <f\5 bes\4 des'\3>1
  <e\5 aes\4 ees'\3>1
  \break
  <f\5 a\4 e'\3>1
  <g\4 des'\3 aes'\2>1
  <d\5 aes\4 des'\3>1
  <d\5 b\4 d'\3>1
  <f\5 a\4 e'\3>1
  <ees\5 aes\4 des'\3>1
  <g\4 des'\3 aes'\2>1
  <f\5 a\4 e'\3>1
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
