from sys import path
from os.path import join, dirname

path.append(join(dirname(__file__), "vendor"))

from .tokenizer import tokenize, to_migaku
