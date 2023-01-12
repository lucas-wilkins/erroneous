from typing import Union
import numpy as np

from encoding_settings import EncodingSettings

EncodableNumber = Union[int, float, np.ndarray]


class NoNumberEncoding(Exception):
    def __init__(self, msg):
        super.__init__(msg)


class CannotEncode(Exception):
    def __init__(self, msg):
        super.__init__(msg)


def encode_numeric(number: EncodableNumber):
    """ Encode numeric data """
    if isinstance(number, int):
        return encode_numeric(np.array(number, dtype=np.float32))
    elif isinstance(number, float):
        return encode_numeric(np.array(number, dtype=np.int32))
    elif isinstance(number, np.ndarray):
        return _encode_numpy_array(number)
    else:
        raise NoNumberEncoding(f"Cannot encode numbers of type {type(number)}")


def _encode_int(x: int):
    return x.to_bytes(EncodingSettings.number_encoding_depth, EncodingSettings.endianness)



def _encode_numpy_array(arr: np.ndarray):
    """ Main part of encoding numeric data

    [      0    |   1234567    ] [4 bytes x (shape length)] [ data length ]
    [ int/float | shape length ] [         shape          ] [    data     ]

    """

    # Is it an int array or a float array
    if arr.dtype.kind == "i":
        int_float_flag = 0
        arr = arr.astype(np.int32)
    elif arr.dtype.kind == "f":
        int_float_flag = 1
        arr = arr.astype(np.float32)
    else:
        raise NoNumberEncoding(f"Cannot encode data of dtype {arr.dtype}")

    # Get length of shape
    shape_length = len(arr.shape)
    if shape_length > 127:
        raise CannotEncode(f"To many dimensions in array ({shape_length})")

    type_byte = (2*shape_length + int_float_flag).to_bytes(1, EncodingSettings.endianness, signed=False)
    shape_bytes = [x.to_bytes(
                    EncodingSettings.dimension_encoding_depth,
                    EncodingSettings.endianness,
                    signed=False) for x in arr.shape]

    data_bytes = arr.tobytes()

    sections = [type_byte] + shape_bytes + [data_bytes]

    return b''.join(sections)

def decode_numeric(data: bytes):
    """
    Decode byte data into int, float or numpy array

    :param data: input bytes to decode
    :return: (decoded, read_size) the decoded data along with the number of bytes read
    """

    # Get the type and shape
    int_float_flag = data[0] & 1
    dtype = np.int32 if int_float_flag == 0 else np.float32

    shape_length = data[0] >> 1

    shape = []
    for i in range(shape_length):
        dim_data = data[1+EncodingSettings.dimension_encoding_depth*i:1+EncodingSettings.dimension_encoding_depth*(i+1)]
        dim = int.from_bytes(dim_data, EncodingSettings.endianness, signed=False)
        # print(dim_data, dim)
        shape.append(dim)

    n_datapoints = 1
    for n in shape:
        n_datapoints *= n

    data_start = 1 + shape_length*EncodingSettings.dimension_encoding_depth
    data_end = data_start + EncodingSettings.number_encoding_depth*n_datapoints

    data_bytes = data[data_start:data_end]

    if len(shape) == 0:
        if int_float_flag == 0:
            # integer
            return int(np.frombuffer(data_bytes, dtype=np.int32)), data_end
        else:
            # float
            return float(np.frombuffer(data_bytes, dtype=np.float32)), data_end

    else:

        if int_float_flag == 0:
            # integer
            unshaped = np.frombuffer(data_bytes, dtype=np.int32)
        else:
            # float
            unshaped = np.frombuffer(data_bytes, dtype=np.float32)

        return unshaped.reshape(tuple(shape)), data_end


if __name__ == "__main__":

    for input in [1,
                  1.0,
                  np.arange(10, dtype=float),
                  np.arange(10, dtype=int),
                  np.zeros((3,3,3)),
                  np.arange(12).reshape((3, 4))]:


        encoded = encode_numeric(input)
        decoded, decode_size = decode_numeric(encoded)

        print(len(encoded), decode_size)
        print(input, decoded)

