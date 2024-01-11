from tokenizer import tokenize, to_migaku, ReadingType

cn_text = "Hello, asdfalskdf 2000佢講嘅政策都係空談，唔會真正幫到草根市民。"
x = tokenize(cn_text, "cn", ReadingType.JYUTPING)
[print(token) for token in x]

print(to_migaku(cn_text, "cn", ReadingType.JYUTPING))
print(to_migaku(cn_text, "cn", ReadingType.JYUTPING))
print(to_migaku(cn_text, "cn", ReadingType.JYUTPING))
print(to_migaku(cn_text, "cn", ReadingType.JYUTPING))
print(to_migaku(cn_text, "cn", ReadingType.JYUTPING))
