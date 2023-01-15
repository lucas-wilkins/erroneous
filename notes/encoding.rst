Binary Representations
======================

When entries have binary representations that are variable in length, they
being with a length specification. Functions that decode an element in the
binary representation therefore return the size of the decoded element which
can then be used to locate the start index of the next element. The functions
that decode are named ``decode_*`` and ``decode_*_with_size``.
