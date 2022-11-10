from expression import Expression

"""

Data Correlation Tokens

"""

def dct_hash(*components, hash_type: int):
    if hash_type == 0:
        # MD5
        pass
    elif hash_type == 1:
        # SHA-2
        pass

    else:
        raise ValueError("Only DCT hash types 0 and 1 are currently supported")

def parseDataCorrelationCode(dcc: str) -> Expression:
    pass

def writeDataCorrelationCode(expr: Expression) -> str:
    return