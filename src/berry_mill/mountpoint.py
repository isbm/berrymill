# Mountpoint collects all mountpoints into one database
# and is globally available as a singleton.
# Plugins and other operations can refer there at any time
# for arbitrary whatever operations they do.
#
# Teardown (unmount) happens at the end of Berrymill cycle.

from __future__ import annotations
from collections import OrderedDict
import kiwi.logger
import time
import os
import tempfile
import shutil

log = kiwi.logging.getLogger('kiwi')
log.set_color_format()


class MountPoint:
    """
    MountPoint in-memory store of all mounted devices.
    Can be imported and instantiated from anywhere
    """
    _instance:MountPoint|None = None

    def __new__(cls) -> MountPoint:
        if cls._instance is None:
            cls._instance = super(MountPoint, cls).__new__(cls)
            cls._instance._mountstore = OrderedDict()
        return cls._instance

    @staticmethod
    def wait_mount(dst:str, umount:bool = False):
        itr = 0
        while True:
            itr += 1
            time.sleep(0.1)
            if itr > 0x400:
                raise Exception("Unable to mount target filesystem")
            elif not umount and os.listdir(dst):
                log.debug("System mounted")
                break
            elif umount and not os.listdir(dst):
                log.debug("System unmounted")
                break


    def mount(self, pth:str, dst:str|None = None) -> str:
        """
        Mount a specific path to a tempdir. If `dst` is not given,
        temporary directory is returned.

        If mount fails, exception is raised.
        """
        mpt = self.get_mountpoint(pth)
        if mpt:
            return mpt

        if not dst:
            dst = tempfile.TemporaryDirectory(prefix="bml-{}-mnt-".format(os.path.basename(pth))).name
        os.makedirs(dst)

        log.debug("Mounting {} as a loop device to {}".format(pth, dst))
        os.system("mount -o loop {} {}".format(pth, dst))

        MountPoint.wait_mount(dst)
        log.debug("Device {} has been mounted successfully".format(pth))

        self._mountstore[pth] = dst

        return dst


    def umount(self, pth:str) -> None:
        """
        Un-mount a specific path and cleanup everything.
        Exception is raised on failure
        """
        log.debug("Umounting {}".format(pth))
        os.system("umount {}".format(pth))

        MountPoint.wait_mount(pth, umount=True)
        log.debug("Directory {} umounted".format(pth))

        shutil.rmtree(pth)


    def get_mountpoints(self) -> list[str]:
        """
        Return mounted filesystems
        """
        return self._mountstore.values()


    def get_mountpoint(self, img:str) -> str|None:
        """
        Return a mount point
        """
        return self._mountstore.get(img)

    def get_image_path(self, mpt:str) -> str|None:
        """
        Get a mounted image location from the existing mountpoint
        """
        for i, m in self._mountstore.items():
            if m == mpt:
                return i


    def flush(self):
        """
        Flush all mounts entirely.
        """
        log.debug("Flushing mountpoints")
        [self.umount(pth) for pth in self._mountstore.values()]
