from tokenizer import tokenize, to_migaku


cn_text = "Hello, world! 😊 こんにちは、世界[shi4 jie4]！🌏 你好[ni3 hao3]，世界[shi4 jie4]！🐉"
x = tokenize(cn_text, "cn")
# [print(token) for token in x]

print(to_migaku(cn_text, "cn"))
