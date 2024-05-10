"""
Some helper functions for encoding and decoding to and from binary and ASCII
"""

def encode(value: str):
    """
    Encode a binary string into a text string.

    Args:
        value (str): A binary string to be encoded.
    Returns:
        str: The encoded text string.
    """

    txt=''.join([chr(int(value, 2)) for value in value.split()])
    return txt

def decode(value: str):
    """
    Decode a text string into a binary string.

    Args:
        value (str): A text string to be encoded.
    Returns:
        str: The decoded binary string.
    """

    txt=' '.join(format(ord(x), 'b') for x in value)
    return txt
