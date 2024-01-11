from logging import ERROR
from .utils import *

# add vendor to path
add_to_path(VENDOR_DIR)

from jieba import setLogLevel

setLogLevel(ERROR)

from .tokenizer import gen_display_format, strip_display_format, tokenize
