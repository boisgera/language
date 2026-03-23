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
$c \in V \mapsto p \in D$ per se, but rather a function $f$ that
associates to any clue $c$ a an estimate of the probability distribution for the password $p$ given the clue $c$.
If you have the probability distribution, you can always find the word $p$ that maximizes $\mathbb{P}(p|c)$ afterwards anyway.

Now, instead of probabilities, consider scores, defined as 
(unnormalized) log-probabilities: for any $c$, $w \mapsto s(w|c)$
such that

$$
\mathbb{P} (p|c) = \frac{\exp {s(p|c)}}{\sum_{w \in V} \exp{s(w|c)}}.
$$

You can always normalize a score to get a true log-probability with the
formula

$$
\log \mathbb{P}(p|c) = s(p|c) - \log \sum_{w \in V} \exp s(w|c).
$$


Let's say that you have a large database of (successfully guessed) clue / password pairs and that you produce a predictor $s$ that associates to
score $s(p|c)$ for the password $p$ given the clue $c$. To each score
function $s(\cdot|c)$ you can associate a log-probability by the 
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
s_i := s(w_i|c), \quad i=0,\dots, n-1.
$$

The partial derivative of 
$s(p|c) - \log \sum_{k=0}^{n-1} \exp s_k$ with respect to $s_i$ is

$$
\{w_i = p\} - \frac{\exp s(w_i|c)}{\sum_{k=0}^{n-1} \exp s(w_k|c)}
$$

Taking the $\mathbb{E}[\cdot | c]$ of this expression yields

$$
\mathbb{P}(w_i|c) - \frac{\exp s(w_i|c)}{\sum_{k=0}^{n-1} \exp s(w_k|c)}
$$

which is null (for a maximum of minus the conditional loss) when
the predictor scores, interpreted as probabilities, match the conditional
probabilities of the password given a context word!

In other words, with a free predictor architecture ($n \times n$
free parameters) which is optimal, the prediction scores $s(p|c)$ 
reinterpreted as probabilities (by exponentiation and normalization)
match the "true" conditional probabilities $\mathbb{P}(p|c)$.

**Nota.** At first, I was thinking that in the realm of non-free architecture,
one could introduce a $d \leq n$ and an embedding matrix 
$$
E = [e_0, e_1, \dots, e_{d-1}] \in \mathbb{R}^{d \times n}
$$
such that the score associated the word $c=w_j$ is
$$
s(w_i|w_j) = [E^t \cdot E]_{i j} = e_j^t e_i.
$$

But with this approach, since $E^t \cdot E$ is symmetric, 
we would have structurally $s(w_i|w_j) = s(w_j|w_i)$ when the "optimal"
predictor has not such symmetry in general, since

$$
\mathbb{P}(w_i | w_j) \neq \mathbb{P}(w_j | w_i)
$$

unless $\mathbb{P}(w_i) = \mathbb{P}(w_j)$. Therefore, it makes more sense
when the cross-entropy is used as a loss to provision an encoder matrix
and a decoder matrix

$$
E \in \mathbb{R}^{d \times n}, \quad
F \in \mathbb{R}^{n \times d}
$$

such that

$$
s(w_i|w_j) = [F \cdot E]_{i j}.
$$

Then, of course what are the "embeddings" of a word is more mysterious
since two different vectors now play this role ... Which pleads strongly
for a revision of the loss criteria in order to restore the symmetry! 
What we want ultimately is a criteria which in a free architecture
is optimal when $s(w_i|w_j)$ matches the PMI of $w_i$ and $w_j$, 
up to a constant (because in a symmetric encoder-decoder architecture,
that will yield "king - queen = man - woman").

At this stage, need to have a look at the SGNS (ski-gram negative sampling)
criteria/literature.




[Password]: https://en.wikipedia.org/wiki/Password_(American_game_show)


## Negative Sampling

In the guessing game, you have one shot to guess an unknown word given a 
context word and you score if your guess is correct.
For example, given the context "ice", it's sensible to guess "cold" or 
"cream". We have recorded a huge dataset of such games and now we'd like
to find a suitable predictor.

Specifically, we wish to find the best "free architecture" score model: 
for any pair of word $(w, c)$ we can select any real value $s(w, c)$
as the score of the guess $w$ given the context $c$.

Pick randomly a pair $(w, c)$ and, independently, 
an extra context word $c'$; the loss $\ell$ associated to these samples is
defined as
$$
\ell := a(-s(w, c)) + a(s(w, c')), \qquad
a(x) := \log(1 + e^x).
$$

What model minimizes the expectation of $\ell$?

-----

We have 

\begin{align*}
\mathbb{E} \, \ell
&=
\sum_{w, c} \mathbb{P}(w \wedge  c) a(-s(w, c)) 
+ 
\sum_{w, c} \mathbb{P} (w) \mathbb{P}(c) a(s(w, c)) \\
&= 
\sum_{w, c} 
\mathbb{P}(w) \mathbb{P}(c) 
\left[ \frac{\mathbb{P}(w,  c)}{\mathbb{P}(w) \mathbb{P}(c)} a(-s(w, c)) + a(s(w, c)) \right]
\end{align*}

Remember that 
$$
\mathrm{PMI}(w, c) := \log \frac{\mathbb{P}(w,  c)}{\mathbb{P}(w) \mathbb{P}(c)} 
$$

To maximize the sum, we have to maximize it wrt each $x = s(w, c)$ and since
we have a sum of positively weighted terms, search for the solution to:

$$
\operatorname*{arg\,max}_x \, (\exp \mathrm{PMI}(w, c)) a(-x) + a(x).
$$

If we differentiate the expression wrt $x$, we get:

$$
\exp \mathrm{PMI}(w, c) \left(-\frac{e^{-x}}{1 + e^{-x}} \right)  + \frac{e^x}{1 + e^{x}}
$$

Equate this to 0 and you get

$$
\exp \mathrm{PMI}(w, c) = \frac{e^x}{1 + e^{x}} \frac{1 + e^{-x}}{{e^{-x}}}
= \frac{e^x + 1}{e^{-x} + 1} = e^x
$$

and thus

$$
x = \mathrm{PMI}(w, c).
$$

Yay! The optimal scorer wrt the weird loss we have introduced is:

$$
s(w, c) = \mathrm{PMI}(w, c) = \log \frac{\mathbb{P}(w,  c)}{\mathbb{P}(w) \mathbb{P}(c)}. 
$$