import numpy as np
import unittest
from hypothesis import given, strategies as st
from typing import Union, List, Optional, Tuple

from encoding import EncodingSettings, EncodingError

from hypothesis.extra.numpy import arrays, array_shapes

from expression import Expression, Constant, Variable, Plus, Neg
from expression import encode_variable_table, decode_variable_table_with_size
from parsing import parse_expression


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

    @given(
        data=st.one_of(
            st.integers(
                min_value=EncodingSettings.min_encodable_signed_int,
                max_value=EncodingSettings.max_encodable_signed_int),
            st.floats()),
        padding=st.binary())

    def test_encode_decode_constant_no_table(self, data: Union[int, float], padding: bytes):
        expr = Constant(data)
        encoded = expr._serialise({}) + padding
        decoded, _ = Expression._deserialise_with_size(encoded, [])

        self.assertEqual(expr.pretty_print_string(), decoded.pretty_print_string())


    @given(
        data=st.one_of(
            st.integers(
                min_value=EncodingSettings.min_encodable_signed_int,
                max_value=EncodingSettings.max_encodable_signed_int),
            st.floats()),
        padding=st.binary())

    def test_encode_decode_constant(self, data: Union[int, float], padding: bytes):
        expr = Constant(data)
        encoded = expr.serialise() + padding
        decoded = Expression.deserialise(encoded)

        self.assertEqual(expr.pretty_print_string(), decoded.pretty_print_string())


    @given(
        data=st.one_of(
            st.integers(
                min_value=EncodingSettings.min_encodable_signed_int,
                max_value=EncodingSettings.max_encodable_signed_int),
            st.floats()),
        padding=st.binary())

    def test_encode_decode_neg_no_table(self, data: Union[int, float], padding: bytes):
        expr = Neg(Constant(data))
        encoded = expr._serialise({}) + padding
        decoded, _ = Expression._deserialise_with_size(encoded, [])

        self.assertEqual(expr.pretty_print_string(), decoded.pretty_print_string())


    @given(
        identity=st.binary(min_size=1),
        print_alias=st.text(min_size=1) | st.none(),
        padding=st.binary())
    def test_encode_decode_single_variable(self, identity: bytes, print_alias: Optional[str], padding: bytes):
        expr = Variable(identity, print_alias=print_alias)
        encoded = expr._serialise({}) + padding
        decoded, _ = Expression._deserialise_with_size(encoded, [])


    test_expressions = [
        parse_expression("x^2 + 1"),
        parse_expression("a+b+c"),
        parse_expression("10*(p+q)/(p-q)")
    ]

    def test_encode_decode_expression(self):
        for expression in self.test_expressions:
            encoded = expression.serialise()
            decoded = Expression.deserialise(encoded)

            # print(decoded)

if __name__ == "__main__":
    unittest.main()