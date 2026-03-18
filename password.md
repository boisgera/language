The Password Game
================================================================================

In [Password], you have to guess a word (the password) given another word
(the clue). Let's predict the password using machine learning!

To begin with, both words belong to a large but finite vocabulary $V$ of size
$n$. Let $w_i$ be the word associated to the index $i \in \{0, \dots, n-1}$.

There is an immediate issue: there is no single "right answer" for a clue,
but instead several answers that are more or less likely. In other words,
what we search for is not directly a mapping 
$c \in V \mapsto p \in D$ but rather a function that
associates to any clue $c$ a probability distribution for the password $p$
given the clue $c$:

$$
c \in V \mapsto \left\(p \in V \mapsto \mathbb{P}(p|c)\right\).
$$





[Password]: https://en.wikipedia.org/wiki/Password_(American_game_show)