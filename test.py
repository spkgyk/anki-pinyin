from tokenizer import tokenize, to_migaku


cn_text = "请你别跑来跑去，坐稳扶好"
print(to_migaku(cn_text, "cn"))

jp_text = "あんた方はデーン人ですな？なかなか達者なイングランド語を話されるが…少し訛っていらっしゃる。"
output = tokenize(jp_text, "jp")
# [print(o) for o in output]

print(to_migaku(jp_text, "jp"))
