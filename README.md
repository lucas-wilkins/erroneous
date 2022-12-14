 
Erroneous: Tracking Statistical Dependencies, Calculating Better Errors
=======================================================================

Erroneous has multiple components
* A token system for tracking statistical dependencies: Data Correlation Tokens (DCTs)
  * [A specification for tokens](schema/dct-0.rst)
  * Token readers and writers
* Tools for making use of this tracking data, and providing related functionality
  * Calculating standard errors
  * Stochastic error calculations
  * A basic symbolic calculator
  * Abstract classes for projects that wish to leverage DCTs

The Problem
===========

Example
-------

The problem *erroneous* solves is best illustrated by a problem that occurs with 
the standard approach to propagating errors, which is to calculate a new variance
whenever you perform a calculation.

Consider two variables, $a$ and $b$ with standard deviations $\sigma_a$ and $\sigma_b$.
Add these together to get $x = a+b$ and the calculated standard deviation of $x$ using the
standard error propagation rules will be $\sigma_x = \sqrt{\sigma_a^2 + \sigma_b^2}$.

All good up to this point.

Now lets take $b$ away from $x$.

$y = x - b$

Again, we have an error propagation formula, $\sigma_y = \sqrt{\sigma_x^2 + \sigma_b^2}$. 
But this calculation gives a standard deviation of $y$ as:

$\sigma_y = \sqrt{\sigma_x^2 + \sigma_b^2} = \sqrt{\sigma_a^2 + 2\sigma_b^2}$.

But we know this is wrong, because $y = a$, so $\sigma_y$ should be equal to $\sigma_a$!

Why does this happen?
---------------------

Fundamentally it is because $b$ and $x$ are not statistically independent and out calculations
did not account for this.

$a$ and $b$ were statistically independent and the error propagation rule was correct,
but $x$ depends on $b$ (being the sum of $a$ and $b$).
Because of this wrong formula was used because our calculation forgot that
$x$ was dependent on $b$.


A Solution
==========

You only need to save a token

Example, with the two $a$ and $b$ variables from before, lets make two derived datasets:

$p = a - b$ which will have a variance of $\sigma_a^2 + \sigma_b^2$
$q = b - a$ which will have a variance of $\sigma_a^2 + \sigma_b^2$

Now we can save these datasets, throwing away the original data, but saving the DCT with them,
then if we load them we can calculate difference, which should be zero

$d = p - q$ and find that $\sigma_d = 0$

WOHOOO!

A Standard
==========

Scope: DCTs are intended to be used on data represents functional relationships, i.e. data which specifies
(non-unique) output values for a list of (unique) input values, with errors and other statistical moments 
(the latter being a more experimental future path).


Data Integrity
==============



Guiding Principles
==================

* It should not try to do too much. Nothing can do all maths. It cannot represent all maths.
