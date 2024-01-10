from tokenizer import tokenize, to_migaku


cn_text = "Hello, world! 😊 こんにちは、世界！🌏 你好，世界！🐉"
x = tokenize(cn_text, "cn")
[print(token) for token in x]

print(to_migaku(cn_text, "cn"))
