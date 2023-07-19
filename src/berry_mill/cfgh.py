import copy


class ConfigHandler:
    def __init__(self, cf_path: str = ""):
        """
        """
        self.__conf = {}

    @property
    def config(self) -> dict:
        return copy.deepcopy(self.__conf)

