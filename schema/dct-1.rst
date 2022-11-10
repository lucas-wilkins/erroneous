Data Correlation Tokens
=======================

Schema Version 1
================

Overall Structure

The DCT is a string, beginning with the prefix `dct_` and followed by the following data in
base 64 format.

.. list-table::

   * - Version (0x01)
   * - N Datasets (2 bytes)
   * - Dataset Hashes (variable)
   * - Contributions of each dataset to moments (variable)

