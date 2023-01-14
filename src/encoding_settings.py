# Serialisation parameters

import numpy as np

class EncodingSettings:
    endianness = 'big'
    variable_index_bytes = 2      # 65536 possible variables
    expression_bytes = 1          # 256 possible objects in expressions
    dimension_encoding_depth = 4  # 4x8 = 32 bit values for dimension sizes
    int_bytes = 4                 # 32 bit ints
    int_dtype = np.int32
    float_bytes = 8               # 64 bit floats
    float_dtype = np.float64
    bytestring_length_bytes = 4   # 32 bits - 4GB of data max

    bytestring_max_length = 256**bytestring_length_bytes
