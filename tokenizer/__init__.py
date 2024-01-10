from logging import ERROR
from .utils import *

# add vendor to path
add_to_path(VENDOR_DIR)

from jieba import setLogLevel

setLogLevel(ERROR)

from .tokenizer import tokenize, to_migaku
