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
  system-system-spacing.basic-distance = #18
  indent = 0
}

% Chord names
chordNames = \chordmode {
  aes1:maj7
  f1:m7
  des1:maj7
  ees2:sus4
  ees2:7
  aes1:maj7
  bes1:m7
  ges1:maj7
  c2:m7
  f2:m7
  b1:maj7
  e1:maj7
  bes1:m7
  ees1:7
  aes1:maj7
  f1:m7
  des2:maj7
  des2:m
  aes1:maj7
  }

% Main notation
notation = \relative c' {
  \clef "treble_8"
  \key aes \major
  \time 4/4
  
  \mark \markup { \box "A" }
  <aes c' g'>1
  <f aes ees'>1
  <c' f' cis''>1
  <ees aes cis'>2
  <ees g cis'>2
  <aes c' g'>1
  <bes cis' aes'>1
  <f bes cis'>1
  <ees bes c'>2
  <f aes ees'>2
  \break
  \mark \markup { \box "B" }
  <ees bes ees'>1
  <e aes ees'>1
  <bes cis' aes'>1
  <ees g cis'>1
  \mark \markup { \box "A'" }
  <aes c' g'>1
  <f aes ees'>1
  <c' f' cis''>2
  <e aes cis'>2
  <aes c' g'>1
  \bar "|."
}

% TAB notation  
tabNotation = \relative c {
  \clef "moderntab"
  \key aes \major
  \time 4/4
  
  <aes\4 c'\3 g'\2>1
  <f\5 aes\4 ees'\3>1
  <c'\3 f'\2 cis''\1>1
  <ees\5 aes\4 cis'\3>2
  <ees\5 g\4 cis'\3>2
  <aes\4 c'\3 g'\2>1
  <bes\4 cis'\3 aes'\2>1
  <f\5 bes\4 cis'\3>1
  <ees\5 bes\4 c'\3>2
  <f\5 aes\4 ees'\3>2
  \break
  <ees\5 bes\4 ees'\3>1
  <e\5 aes\4 ees'\3>1
  <bes\4 cis'\3 aes'\2>1
  <ees\5 g\4 cis'\3>1
  <aes\4 c'\3 g'\2>1
  <f\5 aes\4 ees'\3>1
  <c'\3 f'\2 cis''\1>2
  <e\5 aes\4 cis'\3>2
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
      \override SpacingSpanner.common-shortest-duration = #(ly:make-moment 1/1)
    }
  }
}
