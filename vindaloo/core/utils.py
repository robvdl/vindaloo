import os
import binascii


def random_key_generator(length):
    """
    Generate a new secret key using length given.
    """
    return binascii.hexlify(os.urandom(length)).decode('utf-8')
