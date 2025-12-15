\version "2.24.0"

\header {
  title = "Crystal Silence - Shell Voicing Map"
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
  a1:maj7
  fis1:m7
  d1:maj7
  e1:maj7
  a1:maj7
  cis1:m7
  b1:m7
  e2:sus4 e2:7
  f1:maj7
  g1:maj7
  a1:maj7
  d1:maj7
  b1:m7
  e1:sus4
  a1:maj7
  a1:maj7
}

notation = {
  \clef "treble_8"
  \key a \major
  \time 4/4
  
  \mark \markup { \box "A" }
  <d aes des'>1
  <b d' aes'>1
  <g d' f'>1
  <e aes d'>1
  <d aes des'>1
  <b e' ges'>1
  <a d' e'>1
  <e a d'>2 <e aes d'>2
  \break
  \mark \markup { \box "B" }
  <f a e'>1
  <d b d'>1
  <d aes des'>1
  <g d' f'>1
  \mark \markup { \box "A'" }
  <a d' e'>1
  <e a d'>1
  <d aes des'>1
  <d aes des'>1
  \bar "|."
}

tabNotation = {
  <d\5 aes\4 des'\3>1
  <b\4 d'\3 aes'\2>1
  <g\4 d'\3 f'\2>1
  <e\5 aes\4 d'\3>1
  <d\5 aes\4 des'\3>1
  <b\4 e'\3 ges'\2>1
  <a\4 d'\3 e'\2>1
  <e\5 a\4 d'\3>2 <e\5 aes\4 d'\3>2
  \break
  <f\5 a\4 e'\3>1
  <d\5 b\4 d'\3>1
  <d\5 aes\4 des'\3>1
  <g\4 d'\3 f'\2>1
  <a\4 d'\3 e'\2>1
  <e\5 a\4 d'\3>1
  <d\5 aes\4 des'\3>1
  <d\5 aes\4 des'\3>1
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
