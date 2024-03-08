class PluginException(Exception):
    """
    Plugins should raise this exception anywhere it makes sense
    """

    def __init__(self, id: str, m: str) -> None:
        super().__init__(f"Plugin {id} error: {m}")
