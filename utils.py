import argparse

MINIMUM_VALUE = 5

def check_positive(value):
    """ Check if value is a positive integer, if not raise exception to argparse"""
    try:
        value = int(value)
    except ValueError:
        raise argparse.ArgumentTypeError("%s is not an int value" % value)
    else:
        if value < 0:
            raise argparse.ArgumentTypeError("%s is not a positive int value" % value)
    
    return value

def check_minimum_restricted_integer(value):
    """ Check if value is a positive integer, if not raise exception to argparse"""
    try:
        value = int(value)
    except ValueError:
        raise argparse.ArgumentTypeError("%s is not an int value" % value)
    else:
        if value < MINIMUM_VALUE:
            raise argparse.ArgumentTypeError("%s is below minimum value %s" % value, MINIMUM_VALUE)
    
    return value

def check_restricted_float(value):
    """ Check if value is a integer in a restricted interval, if not raise exception to argparse"""
    try:
        value = float(value)
    except ValueError:
        raise argparse.ArgumentTypeError("%s is not an float value" % value)
    else:
        if value < 0 or value > 1.0:
            raise argparse.ArgumentTypeError("%s not in range [0.0, 1.0]" % value)
    
    return value