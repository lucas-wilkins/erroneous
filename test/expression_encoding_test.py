import numpy as np
import unittest
from hypothesis import given, strategies as st
from typing import Union, List, Optional, Tuple

from encoding import EncodingSettings, EncodingError

from hypothesis.extra.numpy import arrays, array_shapes

from expression import encode_variable_table, decode_variable_table_with_size


class TestExpressionEncoding(unittest.TestCase):

    @given(
        data=st.lists(
            st.tuples(
                st.binary(min_size=1),
                st.text(min_size=1) | st.none())),
        padding=st.binary())

    def test_encode_decode_variable_table(self, data: List[Tuple[bytes, Optional[str]]], padding):

        print(data)

        encoded = encode_variable_table(data)
        decoded, size = decode_variable_table_with_size(encoded + padding)

        self.assertEqual(None, None)

        self.assertEqual(len(data), len(decoded))

        for (a1, a2), (b1, b2) in zip(data, decoded):
            self.assertEqual(a1, b1)
            self.assertEqual(a2, b2)


if __name__ == "__main__":
    unittest.main()