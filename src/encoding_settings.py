# Serialisation parameters

class EncodingSettings:
    endianness = 'big'
    variable_index_bytes = 2      # 65536 possible variables
    expression_bytes = 1          # 256 possible objects in expressions
    dimension_encoding_depth = 4  # 4x8 = 32 bit values for dimension sizes
    number_encoding_depth = 4     # 4x8 = 32 bit values for numeric encoding

