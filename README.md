# erroneous
A python tool for tracking statistical dependencies and calculating better errors

The Problem
===========

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


A Standard
==========



Data Integrity
==============






What it can't be:
 * Something that can do all maths. Nothing can do that.