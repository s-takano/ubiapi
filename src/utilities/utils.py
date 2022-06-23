import logging

def get_logger(name):
    l = logging.getLogger(name)
    l.setLevel(logging.DEBUG)
    return l
