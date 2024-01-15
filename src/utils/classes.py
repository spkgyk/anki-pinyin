from .enums import OutputMode


class FieldOutputModeList(dict[str, OutputMode]):
    def __init__(self, field_mode_dict: dict[str, str]):
        super().__init__({field: OutputMode(mode) for field, mode in field_mode_dict.items()})

    def to_set_text(self):
        return "Already selected fields:\n" + ", ".join(("{} ({})".format(field, output_mode.value) for field, output_mode in self.items()))
