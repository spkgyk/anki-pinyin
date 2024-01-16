from .enums import OutputMode


class FieldOutputModeDict(dict[str, OutputMode]):
    def __init__(self, field_mode_dict: dict[str, str]):
        super().__init__({str(field): OutputMode(mode) for field, mode in field_mode_dict.items()})

    def to_set_text(self):
        return "Already selected fields:\n" + ", ".join(("{} ({})".format(field, output_mode.value) for field, output_mode in self.items()))

    def to_json(self):
        return {field: output_mode.value for field, output_mode in self.items()}


class ToneColorDict(dict[int, str]):
    def __init__(self, tone_color_dict: dict[str, str]):
        super().__init__({int(tone): str(color) for tone, color in tone_color_dict.items()})

    def to_json(self):
        return {str(tone): str(color) for tone, color in self.items()}
