import platform
import os
from typing import Dict
import kiwi.logger

archfix: Dict[str, str] = {
    "x86_64": "amd64",
    "aarch64": "arm64",
}

log = kiwi.logging.getLogger("kiwi")


def get_local_arch() -> str:
    """
    Return the local arch for Debian
    """
    p = platform.processor()
    return archfix.get(p) or p


def has_virtualization() -> bool:
    """
    Returns True if a nested virtualization checks passed.
    """

    # Intels/AMDs only
    if platform.processor() != "x86_64":  # also AMD
        log.error("Only x86_64 architecture is supported at the moment")
        return False

    # CPU supports VM
    with open("/proc/cpuinfo") as fr:
        if not [l for l in fr.readlines() if "vmx flags" in l]:
            log.error("CPU does not have vmx flags")
            return False

    # KVM module loaded?
    mods = [x.split(" ")[0] for x in os.popen("lsmod").readlines()[1:]]
    if "kvm_intel" not in mods and "kvm_amd" not in mods:
        log.error("No KVM kernel module loaded")
        return False

    # Nested is enabled in kvm_* module?
    nested: bool = False
    for m in ["intel", "amd"]:
        if [x for x in os.popen("modinfo kvm_{}".format(m)) if "nested" in x]:
            nested = True
            break
    if not nested:
        log.error("KVM module does not support nested virtualisation")
        return False

    # Nested virtualisation enabled system-wide
    kvm_np: str = "/sys/module/kvm_{}/parameters/nested"
    kvm_np = kvm_np.format("intel") if os.path.exists(kvm_np.format("intel")) else kvm_np.format("amd")
    with open(kvm_np) as fr:
        if fr.read().strip() not in ["y", "Y", "1"]:
            log.error("Nested virtualisation is not enabled")
            return False

    return True

def is_vm() -> bool:
    """
    Detect if the current machine is a VM
    """
    lshw:str = "/usr/bin/lshw"
    assert os.path.exists(lshw), f"{lshw} utility is missing"

    # Crude test on vendors
    vendors:list[str] = set(filter(None, map(lambda l:l.startswith("vendor:")
                                             and l.split(":")[-1].strip()
                                             or "", [x.strip().lower() for x in
                                                     os.popen(f"{lshw} 2> /dev/null").readlines()])))
    for v in ["qemu", "virtualbox", "vmware"]:
        if v in vendors:
            return True

    return False
