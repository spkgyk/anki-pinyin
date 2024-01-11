from logging import ERROR
from jieba import setLogLevel

setLogLevel(ERROR)
from .tokenizer import gen_display_format, strip_display_format, tokenize
