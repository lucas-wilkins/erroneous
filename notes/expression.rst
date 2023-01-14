Notes on Expression and Subclasses
==================================


Variable
--------

The `Variable` class has an `identity`, which is
the unique identifier, but also has a `print_alias`.

The identifier might be complex, but the `print_alias`
is a simple representation for aesthetic purposes.
It is possible, in theory, that `print_alias` values
conflict, however these are low priority, and might
get lost.
