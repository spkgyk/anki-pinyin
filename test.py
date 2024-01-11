from tokenizer import tokenize, gen_display_format, ReadingType

cn_text = "Hello, asdfalskdf 2000佢講嘅政策都係空談，唔會真正幫到草根市民。"
x = tokenize(cn_text, "cn", ReadingType.JYUTPING)
[print(token) for token in x]

print(gen_display_format(cn_text, "cn", ReadingType.JYUTPING))
print(gen_display_format(cn_text, "cn", ReadingType.JYUTPING))
print(gen_display_format(cn_text, "cn", ReadingType.JYUTPING))
print(gen_display_format(cn_text, "cn", ReadingType.JYUTPING))
print(gen_display_format(cn_text, "cn", ReadingType.JYUTPING))
