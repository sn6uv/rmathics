Differences to Mathematica
==========================

Parsing
-------
When parsing real numbers only the bits of precision can be specified.
The following is invalid rmathics code::

    1.5``20  (* 20 digits of accuracy in MMA, invalid in rmathics *)

while::

    1.5`20  (* 20 digits of precision in MMA, 20 bits of precision in rmathics *)

represents something different in rmathics to what it means to Mathematica.
In rmathics the above is a real number with 20 *bits* of precision (not digits!).

Numerical Evaluation
--------------------
Mathematica tracks loss of precision throughout calcuations while rmathics
simply performs calculations with the specified bits of precision.
