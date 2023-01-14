from typing import Union, Tuple
import numpy as np

from encoding import EncodingSettings, EncodingError, DecodingError

EncodableNumber = Union[int, float, np.ndarray]


class NoNumberEncoding(Exception):
    def __init__(self, msg):
        super.__init__(msg)


def encode_numeric(number: EncodableNumber):
    """ Encode numeric data """
    if isinstance(number, int):
        return encode_numeric(np.array(number, dtype=EncodingSettings.int_dtype))
    elif isinstance(number, float):
        return encode_numeric(np.array(number, dtype=EncodingSettings.float_dtype))
    elif isinstance(number, np.ndarray):
        return _encode_numpy_array(number)
    else:
        raise NoNumberEncoding(f"Cannot encode numbers of type {type(number)}")


def _encode_int(x: int):
    return x.to_bytes(EncodingSettings.int_bytes, EncodingSettings.endianness)



def _encode_numpy_array(arr: np.ndarray):
    """ Main part of encoding numeric data

    [      0    |   1234567    ] [4 bytes x (shape length)] [ data length ]
    [ int/float | shape length ] [         shape          ] [    data     ]

    """

    # Is it an int array or a float array
    if arr.dtype.kind == "i":
        int_float_flag = 0
        arr = arr.astype(EncodingSettings.int_dtype)
    elif arr.dtype.kind == "f":
        int_float_flag = 1
        arr = arr.astype(EncodingSettings.float_dtype)
    else:
        raise NoNumberEncoding(f"Cannot encode data of dtype {arr.dtype}")

    # Get length of shape
    shape_length = len(arr.shape)
    if shape_length > 127:
        raise EncodingError(f"To many dimensions in array ({shape_length})")

    type_byte = (2*shape_length + int_float_flag).to_bytes(1, EncodingSettings.endianness, signed=False)
    shape_bytes = [x.to_bytes(
                    EncodingSettings.dimension_encoding_depth,
                    EncodingSettings.endianness,
                    signed=False) for x in arr.shape]

    data_bytes = arr.tobytes()

    sections = [type_byte] + shape_bytes + [data_bytes]

    return b''.join(sections)


def decode_numeric(data: bytes):
    return decode_numeric_with_size(data)[0]


def decode_numeric_with_size(data: bytes):
    """
    Decode byte data into int, float or numpy array

    :param data: input bytes to decode
    :return: (decoded, read_size) the decoded data along with the number of bytes read
    """

    # Get the type and shape
    int_float_flag = data[0] & 1
    dtype = EncodingSettings.int_dtype if int_float_flag == 0 else EncodingSettings.float_dtype
    dsize = EncodingSettings.int_bytes if int_float_flag == 0 else EncodingSettings.float_bytes

    shape_length = data[0] >> 1

    shape = []
    for i in range(shape_length):
        a = EncodingSettings.dimension_encoding_depth*i + 1
        b = a + EncodingSettings.dimension_encoding_depth
        dim_data = data[a:b]
        dim = int.from_bytes(dim_data, EncodingSettings.endianness, signed=False)
        shape.append(dim)

    n_datapoints = 1
    for n in shape:
        n_datapoints *= n

    data_start = 1 + shape_length*EncodingSettings.dimension_encoding_depth
    data_end = data_start + dsize*n_datapoints

    data_bytes = data[data_start:data_end]

    unshaped = np.frombuffer(data_bytes, dtype=dtype)

    if len(shape) == 0:
        # Return a python, not numpy object

        if int_float_flag == 0:
            # integer
            return int(unshaped), data_end
        else:
            # float
            return float(unshaped), data_end

    else:
        return unshaped.reshape(tuple(shape)), data_end


def encode_bytestring(data: bytes) -> bytes:
    """ Encode data bytes"""
    n = len(data)
    if n > EncodingSettings.bytestring_length_max:
        raise EncodingError(f"Data too long to encode (length={n}, limit={EncodingSettings.bytestring_length_max})")

    return n.to_bytes(
        EncodingSettings.bytestring_length_bytes,
        EncodingSettings.endianness,
        signed=False) + data


def decode_bytestring_with_size(data: bytes) -> Tuple[bytes, int]:
    """ Decode bytestring object, will stop at the length of the bytestring
        encoded in the data, not at the end of the data string,
        returns the byte string along with the end of encoded string"""

    if len(data) < EncodingSettings.bytestring_length_bytes:
        raise DecodingError(f"Encoded bytestring too short (smaller than length specifier length, {EncodingSettings.bytestring_length_bytes} bytes)")

    data_length = int.from_bytes(
        data[:EncodingSettings.bytestring_length_bytes],
        EncodingSettings.endianness,
        signed=False)

    length = data_length + EncodingSettings.bytestring_length_bytes
    out = data[EncodingSettings.bytestring_length_bytes:length]

    return out, length


def decode_bytestring(data: bytes) -> bytes:
    """ Decode bytestring object, will stop at the length of the bytestring
    encoded in the data, not at the end of the data string"""

    return decode_bytestring_with_size(data)[0]
