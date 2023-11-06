from typing import TypedDict


class KiwiParams(TypedDict):
    """
    Dictionary for Gobal Kiwi Parameters

    Attributes:

        profile (str, Optional): select profile for images that makes use of it.
        debug (bool, Default: False): run in debug mode. This means the box VM stays open and the kiwi log level is set to debug(10).
    """
    profile: str
    debug: bool


class KiwiBuildParams(KiwiParams):
    """
    Dictionary for Build specifc Kiwi Parameters

    Attributes:

        box_memory (str, Default: 8G): specify main memory to use for the QEMU VM (box).
        clean (bool, Default: False): cleanup previous build results prior build.
        cross (bool, Default: False): cross image build on x86_64 to aarch64 target.
        cpu (str, Optional): cpu to use for the QEMU VM (box)
        local (bool, Default: False): run build process locally on this machine. Requires sudo setup and installed KIWI toolchain.
        target_dir (str, Default:/tmp/IMAGE_NAME[.PROFILE_NAME]): store image results in given dirpath.
    """
    box_memory: str
    clean: bool
    cross: bool
    cpu: str
    local: bool
    target_dir: str
    no_accel: bool


class KiwiPrepParams(KiwiParams):
    """
    Dictionary for Prepare specific Kiwi Parameters

    Attributes:

        root (str, Required): Path to create the new root system.
    """
    root: str
    allow_existing_root: bool
