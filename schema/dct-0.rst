Data Correlation Tokens
=======================

Schema Version 0
================

Overall Structure

The DCT is a string, beginning with the prefix `dct_` and followed by the following data in
base 64 format.

.. list-table::

   * - Version (0x00)
   * - N Datasets (2 bytes)
   * - Dataset Hashes (variable)
   * - Process Description (variable)


Base Datasets and Hashes
------------------------

Base datasets are the building blocks of any analysis process.
Each base dataset represented as such in this schema is assumed to be statistically independent of
all the others.

Base datasets are represented by hashes in the DCT. The choice of hash and its size is left unspecified,
as this will depend on the details of the data being used. What is important is that each data set
is deterministic assigned a unique identifier (or one extremely likely to be at least)

.. list-table::

   * - Hash type (2 byte)
     - Hash `length` in bytes (1 byte)
     - Hash data (`length` bytes)

The hash type is intended to not indicate only the hashing algorithm, but also the rest of process used to
calculate the hash. A large range of hash type values is available to allow the future inclusion of 3rd
party processes.

In future schemas it may be possible and worthwhile to allow correlated base datasets.

Process Description
-------------------

The combination and transformation of data is represented as a tree structure, built of the following components


Variable
""""""""

.. list-table::

   * - 0x01
     - Dataset ID (2 bytes)
     - Component (1 byte)


Each dataset contains various `components`, each assigned a number

0) The domain/support of the data, i.e. the "x-axis"
1) The observed values at each value in the domain data, (also can be thought of as the first statistical moment)
2) The errors on the y values (standard deviation, square root of second statistical moment)
3) The third statistical moment
4) The fourth statistical moment
5) ...etc..

In future, an extra value (255) might be added for errors on the domain values

Constant
--------

A numerical constant

.. list-table::

   * - 0x02
     - Value Type (1 bytes)
     - Value `length` in bytes (1 byte)
     - Value Data (`length` bytes)

Unary Operations
----------------

The following components operate on other data, so they have the following form

.. list-table::

   * - ID (1 byte)
     - Child data (variable)

The following is a table of the unary operations and their IDs

.. list-table::

   * - Negation
     - 0x10
   * - Absolute Value
     - 0x11
   * - Sign
     - 0x12
   * - Natural Exponent
     - 0x20
   * - Natural Log
     - 0x21

... more to be added, such as trig


Binary Operations
-----------------


Binary components operate on other data, so they have the following form

.. list-table::

   * - ID (1 byte)
     - LHS data / first arg (variable)
     - RHS data / second arg (variable)

The following is a table of the binary operations and their IDs

.. list-table::

   * - Addition
     - 0x40
   * - Subtraction
     - 0x41
   * - Multiplication
     - 0x42
   * - Division
     - 0x43
   * - Modulo
     - 0x44
   * - Power
     - 0x45

... more to be added