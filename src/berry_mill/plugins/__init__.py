class PluginException(Exception):
    def __init__(self, id: str, m: str) -> None:
        super().__init__(f"Plugin {id} error: {m}")
