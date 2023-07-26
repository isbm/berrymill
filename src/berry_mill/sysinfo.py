import platform
from typing import Dict

archfix:Dict[str,str] = {
    "x86_64": "amd64",
    "aarch64": "arm64",
}

def get_local_arch() -> str:
    """
    Return the local arch for Debian
    """
    p = platform.processor()
    return archfix.get(p) or p
