import base64

"""
Some helper functions for encoding and decoding to and from base64 and ASCII
"""

def encode(value: str):
    """
    Encode a base64 string into a text string.

    Args:
        value (str): A base64 string to be encoded.
    Returns:
        str: The encoded text string.
    """

    sample_string = value
    sample_string_bytes = sample_string.encode("ascii")
    base64_bytes = base64.b64decode(sample_string_bytes)
    base64_string = base64_bytes.decode("ascii")
    return base64_string

def decode(value: str):
    """
    Decode a text string into a base64 string.

    Args:
        value (str): A text string to be encoded.
    Returns:
        str: The decoded base64 string.
    """

    base64_string = value
    base64_bytes = base64_string.encode("ascii")
    sample_string_bytes = base64.b64decode(base64_bytes)
    sample_string = sample_string_bytes.decode("ascii")
    return sample_string