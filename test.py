from src.tokenizer.chinese import ChineseTokenizer
from src.utils import ReadingType

cn_text = "我25岁。"
ct = ChineseTokenizer()
x = ct.tokenize(cn_text, ReadingType.JYUTPING)
[print(token) for token in x]

print(ct.gen_display_format(cn_text, ReadingType.JYUTPING).traditional)
