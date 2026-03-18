The Password Game
================================================================================

In [Password], you have to guess a word (the password) given another word
(the clue). For example, if I tell you "ice", you may be able to guess "cold".

Let's build a password predictor the password using machine learning!

To begin with, both words belong to a large but finite vocabulary $V$ of size
$n$. Let $w_i$ be the word associated to the index $i \in \{0, \dots, n-1\}$.

There is an immediate issue: there is in general no single "right answer" for 
a clue, but instead several answers that are more or less likely. 
Therefore, we focus not on a predictor
$c \in V \mapsto p \in D$ but rather on function that
associates to any clue $c$ a probability distribution for the password $p$
given the clue $c$:

$$
c \in V \mapsto \left\(p \in V \mapsto \mathbb{P}(p|c)\right\).
$$

If you have the probability distribution, you can always perform an
$\argmax$ afterwards to find the word $p$ that maximizes $\mathbb{P}(p|c)$.





[Password]: https://en.wikipedia.org/wiki/Password_(American_game_show)