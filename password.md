The Password Game
================================================================================

In [Password], you have to guess a word (the password) given another word
(the clue). For example, if I tell you "ice", you may be able to guess "cold"
... with some degree of certainty!

Let's build a password predictor using machine learning (science, bitches!).

To begin with, both words belong to a large but finite vocabulary $V$ of size
$n$. Let $w_i$ be the word associated to the index $i \in \{0, \dots, n-1\}$.

There is an immediate issue: there is in general no single "right answer" for 
a clue, but instead several answers that are more or less likely. 
Therefore, we will not build a predictor
$c \in V \mapsto p \in D$ per se, but rather on function that
associates to any clue $c$ a an estimate of the probability distribution for the password $p$ given the clue $c$:

$$
c \in V \mapsto \left(p \in V \mapsto \mathbb{P}(p|c) \in [0, 1]\right).
$$

If you have the probability distribution, you can always find the word $p$ that maximizes $\mathbb{P}(p|c)$ afterwards anyway.

Now, instead of probabilities, consider scores, defined as 
(unnormalized) log-probabilities: for any $c$, any collection of $s(p=w|c)$
such that

$$
\mathbb{P} (p|c) = \frac{\exp {s(p=p|c)}}{\sum_{w \in V} \exp{s(p=w|c)}}.
$$

You can always normalize a score to get a true log-probability with the
formula

$$
\log \mathbb{P}(p|c) = s(p|c) - \log \sum_{w \in V} \exp s(p=w|c).
$$

Let's say that you have a large database of (successfully guessed) clue / password pairs and that you produce a predictor $s$ that associates to
score $s(p|c)$ for the password $p$ given the clue $c$. To each score
you function $s(\cdot|c)$ you can associate a log-probability by the 
substraction of a suitable constant.

Now consider as a loss function the opposite of the expectation of this 
log-probability of $p$ given $c$:

$$
\ell = - \mathbb{E} \left[ s(p|c) - \log \sum_{w \in D} \exp s(w|c) \right] 
$$

What is the optimum funcion $s$ give what we have in our database?
To begin with we can disintegrate the expectation by the value of $c$

$$
\ell = - \mathbb{E}_c \left[ \mathbb{E} \left[s(p|c) - \log \sum_{w \in D} \exp s(w|c) \middle|  c \right]\right]
$$

and note that if we have a complete freedom on the structure of the predictor
$s$, then we have to optimize each term conditionned by $c$ independently to
get the overall optimum. Now, given a $c$, let $s \in \mathbb{R}^n$ be 
the (free) vector of scores:

$$
s_i := s(w_i|c), \;\;\; i=0,\dots, n-1.
$$

The gradient of 
$s - \log \sum_{k=0}^{n-1} \exp s_k$



[Password]: https://en.wikipedia.org/wiki/Password_(American_game_show)