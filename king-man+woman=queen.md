
King - Man + Woman = Queen
================================================================================

Why do concepts map cleanly to vectors in embedding spaces?


Embedding
--------------------------------------------------------------------------------

Each *word* (or more generally *token*) in a finite *vocabulary* of size $n$ 
is identified to an *index* $w \in \{0, \dots, n-1\}$. 
Let $d$ be an *embedding dimension* 
(typically quite large, like 1024, but far smaller than the vocabulary size). 

An embedding $e$ is a function

$$
e : \{0, \dots, n-1\} \to \mathbb{R}^d
$$

(which is likely to span the full vector space).


Pointwise mutual information
--------------------------------------------------------------------------------

The pointwise mutual information $\mathrm{PMI}(a, b)$ is the log-probability
boost that $a$ gets when $b$ is present in the context (understand *context*
as "lexical neighbourhood" of some sort, for example, presence in the same
sentence).

$$
\mathrm{PMI}(a, b) := \log \frac{\mathbb{P}(a | b)}{\mathbb{P}(a)}
$$

(pick any basis you like for the log and stock with it). By definition of
the conditional probability, we also have


$$
\mathrm{PMI}(a, b) = \log \frac{\mathbb{P}(a \wedge b)}{\mathbb{P}(a) \mathbb{P}(b)}
$$

and the definition is symmetric wrt its arguments. 
Hence, our PMI function is a big $n \times n$ symmetric matrix.


King - Man + Woman = Queen
--------------------------------------------------------------------------------

Assume that we want (?) and manage to (?) get some embedding function such
that up to a constant c, we have for any pair of words $a$ and $b$:

$$
\mathrm{PMI}(a, b) + c \approx e(a) \cdot e(b).
$$

(more on this later!). Since the word "king" has the same relation to the word
"man" than the word "queen" has to "woman", it's not too far-fetched to 
assume that for any word $w$ in the vocabulary, we have

$$
\frac{\mathbb{P}(\mathrm{king}|w)}{\mathbb{P}(\mathrm{man}|w)} =
\frac{\mathbb{P}(\mathrm{queen}|w)}{\mathbb{P}(\mathrm{woman}|w)}.
$$

Rewrite that in terms of PMI,

$$
\mathrm{PMI}(\mathrm{king}, w) 
- \mathrm{PMI}(\mathrm{man}, w)
+ \mathrm{PMI}(\mathrm{woman}, w)
= 
\mathrm{PMI}(\mathrm{queen}, w)
$$

or, with embeddings,

$$
\forall \, w \in \{0, \dots, n-1\}, \, 
\left(e(\mathrm{king}) - e(\mathrm{man}) + e(\mathrm{woman}) \right) \cdot e(w) \approx
e(\mathrm{queen}) \cdot e(w).
$$

If the embedding function spans $\mathbb{R}^d$, we can deduce that

$$
e(\mathrm{king}) - e(\mathrm{man}) + e(\mathrm{woman}) 
\approx
e(\mathrm{queen}).
$$

You can also think in the embedding space of the concept of "royalty"

$$
\mathrm{royalty}
:= 
e(\mathrm{king}) - e(\mathrm{man}) 
\approx
e(\mathrm{queen}) - e(\mathrm{woman})
$$

and the concept of (female-to-male) "gender" as:

$$
\mathrm{gender}
:= 
e(\mathrm{man}) - e(\mathrm{woman}) 
\approx
e(\mathrm{king}) - e(\mathrm{queen}).
$$



Embeddings as factorization and low-rank approximation
--------------------------------------------------------------------------------

OK, now we know why having embeddings related to PMI with

$$
\mathrm{PMI}(a, b) + c \approx e(a) \cdot e(b).
$$

for some constant $c$ would be handy to provide a nice semantic structure 
in the embedding space.
How do we achieve this? We know that the $\mathrm{PMI}$ function is a 
symmetric matrix; therefore for a suitable 
$c \in \mathbb{R}$, $\mathrm{PMI} + c$ is symmetric 
positive semidefinite (SPSD) and we can factor it into

$$
\mathrm{PMI} + c = Q^t \mathrm{diag}(\lambda_1, \dots, \lambda_n) Q,
$$

where $Q$ is orthogonal and $\lambda_1 \geq \dots \geq \lambda_n \geq 0$.
If there are some null eigenvalues, we can reduce the dimensionality
from $n$ to $d$ and get

$$
\mathrm{PMI} + c = Q_d^t \mathrm{diag}(\lambda_1, \dots, \lambda_d) Q_d,
$$

where $Q_d^t Q_d = I_d$ and $\lambda_1 \geq \dots \geq \lambda_d > 0$.
(If you don't have that but want to reduce the dimension anyway,
it's time to perform an approximation and say that the lowest eigenvalues
are approximately zero).

Now let $\Lambda := \mathrm{diag}(\lambda_1, \dots, \lambda_d)$. We have

$$
\mathrm{PMI} + c =
Q_d^t \sqrt{\Lambda}^t \sqrt{\Lambda} Q_d
= (\sqrt{\Lambda} Q_d)^t (\sqrt{\Lambda} Q_d)
$$

Defining $e(a)$ is the $a$-th column vector of $\sqrt{\Lambda} Q_r$, 
for any pair of words $a$ and $b$ yields

$$
\mathrm{PMI}(a, b) + c = e(a) \cdot e(b)
$$

as intended.




References
--------------------------------------------------------------------------------

- "king - man + woman is queen; but why?" by Piotr Migdał. URL: 
  <https://p.migdal.pl/blog/2017/01/king-man-woman-queen-why/>