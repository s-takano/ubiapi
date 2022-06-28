import logging
from datetime import datetime
from dateutil import parser

def get_logger(name):
    l = logging.getLogger(name)
    l.setLevel(logging.DEBUG)
    return l

def date_validator(cls, d, is_optional=True):
    if is_optional and d is None:
        return None
    elif isinstance(d, datetime):
        return datetime(d.year, d.month, d.day, d.hour, minute=d.minute, second=d.second, microsecond=d.microsecond, tzinfo=None)
        
    return parser.parse(d, ignoretz=True)

