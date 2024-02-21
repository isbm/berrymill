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

    # CPU supports VM
    with open("/proc/cpuinfo") as fr:
        if not [l for l in fr.readlines() if "vmx flags" in l]:
            log.warning("CPU does not have vmx flags")
            return False

    # KVM module loaded?
    mods = [x.split(" ")[0] for x in os.popen("lsmod").readlines()[1:]]
    if "kvm_intel" not in mods and "kvm_amd" not in mods:
        log.warning("No KVM kernel module loaded")
        return False

    # Nested is enabled in kvm_* module?
    nested: bool = False
    for m in ["intel", "amd"]:
        if [x for x in os.popen("modinfo kvm_{}".format(m)) if "nested" in x]:
            nested = True
            break
    if not nested:
        log.warning("KVM module does not support nested virtualisation")
        return False

    # Nested virtualisation enabled system-wide
    kvm_np: str = "/sys/module/kvm_{}/parameters/nested"
    kvm_np = kvm_np.format("intel") if os.path.exists(kvm_np.format("intel")) else kvm_np.format("amd")
    with open(kvm_np) as fr:
        if fr.read().strip() not in ["y", "Y", "1"]:
            log.warning("Nested virtualisation is not enabled")
            return False

    return True

def is_vm() -> bool:
    """
    Detect if the current machine is a VM
    """
    assert bool(list(filter(None, [os.path.exists("{}/lshw".format(p)) for p in ["/usr/bin", "/usr/sbin", "/sbin", "/bin"]]))), "lshw utility is missing"
    # Crude test on vendors
    vendors:list[str] = set(filter(None, map(lambda l:l.startswith("vendor:")
                                             and l.split(":")[-1].strip()
                                             or "", [x.strip().lower() for x in
                                                     os.popen("lshw 2> /dev/null").readlines()])))
    for v in ["qemu", "virtualbox", "vmware"]:
        if v in vendors:
            return True

    return False
