class BaseToken:
    def _init_from_token(self, token: "BaseToken"):
        for attr, value in vars(token).items():
            setattr(self, attr, value)

    def __str__(self):
        items = [(k, v) for k, v in sorted(self.__dict__.items()) if not k.startswith("_")]
        _max_len = max(len(k) for k, _ in items) + 1
        return_string = f"{self.__class__.__name__}(\n" + "".join(f"""   "{k}":{"":<{_max_len-len(k)}}{v},\n""" for k, v in items) + ")"
        return return_string


class BaseTokenizer:
    def tokenize(self, *args, **kwargs):
        raise NotImplementedError

    def __call__(self, *args, **kwargs):
        return self.tokenize(*args, **kwargs)
