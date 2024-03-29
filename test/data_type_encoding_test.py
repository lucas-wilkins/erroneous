import numpy as np
import unittest
from hypothesis import given, strategies as st
from typing import Union, List

from encoding import EncodingSettings, EncodingError

from hypothesis.extra.numpy import arrays, array_shapes

from data_type_encoding import (
    encode_numeric, decode_numeric,
    encode_bytestring, decode_bytestring_with_size)


class TestDataTypeEncoding(unittest.TestCase):

    @given(
        data=st.binary(),
        padding=st.binary())

    def test_encode_decode_bytes(self, data: bytes, padding: bytes):
        n = len(data)

        if n > EncodingSettings.bytestring_length_max:
            with self.assertRaises(EncodingError):
                encode_bytestring(data)
        else:
            encoded = encode_bytestring(data)
            encoded += padding
            decoded, decoded_length = decode_bytestring_with_size(encoded)

            self.assertEqual(data, decoded)
            self.assertEqual(decoded_length, n + EncodingSettings.bytestring_length_bytes)


    @given(
        st.one_of(
            st.floats(),
            st.integers(
                min_value=-(2**31 - 1),
                max_value=2**31 - 1)))

    def test_encode_decode_scalar(self, data: Union[float, int, np.ndarray]):

        encoded = encode_numeric(data)
        decoded = decode_numeric(encoded)

        self.assertEqual(type(data), type(decoded))
        np.testing.assert_equal(data, decoded)



    @given(
        st.one_of(
            arrays(
                shape=array_shapes(max_dims=4),
                dtype=EncodingSettings.int_dtype),
            arrays(
                shape=array_shapes(max_dims=4),
                dtype=EncodingSettings.float_dtype)))

    def test_encode_decode_numpy(self, data: np.ndarray):

            encoded = encode_numeric(data)
            decoded: np.ndarray = decode_numeric(encoded)

            if len(data) == 1:

                np.testing.assert_equal(data, decoded)

            else:

                self.assertEqual(data.dtype, decoded.dtype)
                self.assertEqual(len(data.shape), len(decoded.shape))
                for n, m in zip(data.shape, decoded.shape):
                    self.assertEqual(n, m)

                np.testing.assert_almost_equal(data, decoded)


if __name__ == "__main__":
    unittest.main()