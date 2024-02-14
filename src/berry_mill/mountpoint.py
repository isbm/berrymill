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
from berry_mill.imagefinder import ImagePtr


log = kiwi.logging.getLogger('kiwi')
log.set_color_format()


class MountPoint:
    """
    MountPoint holds all the information about an object,
    whether it is a single simple image or a partitioned disk device.
    """

    def __init__(self) -> None:
        self._partitions:set[str] = set()

    def add(self, pth) -> MountPoint:
        self._partitions.add(pth)
        return self

    def get_partitions(self) -> list[str]:
        """
        Return mounted partitions
        """
        return tuple(self._partitions)

class MountManager:
    """
    MountManager is an in-memory store of all mounted devices.
    Can be imported and instantiated from anywhere
    """
    _instance:MountManager|None = None

    def __new__(cls) -> MountManager:
        if cls._instance is None:
            cls._instance = super(MountManager, cls).__new__(cls)
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


    def __mount_partition_image(self, pth:str) -> str:
        """
        Mount a single partition image, return mounted directory
        """
        mpt = self.get_mountpoint(pth)
        if mpt:
            return mpt

        dst:str = tempfile.TemporaryDirectory(prefix="bml-{}-mnt-".format(os.path.basename(pth))).name
        os.makedirs(dst)

        log.debug("Mounting {} as a loop device to {}".format(pth, dst))
        os.system("mount -o loop {} {}".format(pth, dst))

        MountManager.wait_mount(dst)
        log.debug("Device {} has been mounted successfully".format(pth))
        self._mountstore[pth] = MountPoint().add(dst)

        return dst

    def __mount_disk_image(self, imptr:ImagePtr) -> None:
        """
        Mount a partitioned disk image
        """
        # Get a list of partitions

        # Setup loops

        # Mount each partition/loop to its own target

        raise NotImplementedError("Partitioned image mounts is not implemented yet")

    def mount(self, img_ptr:ImagePtr) -> str:
        """
        Mount a specific path to a tempdir. If `dst` is not given,
        temporary directory is returned.

        If mount fails, exception is raised.
        """

        if img_ptr.img_type == ImagePtr.PARTITION_IMAGE:
            return self.__mount_partition_image(img_ptr.path)
        elif img_ptr.img_type == ImagePtr.DISK_IMAGE:
            return self.__mount_disk_image(img_ptr.path)

        raise Exception("Unable to mount image: {}".format(repr(img_ptr)))

    def umount(self, pth:str) -> None:
        """
        Un-mount a specific path and cleanup everything.
        Exception is raised on failure
        """
        log.debug("Umounting {}".format(pth))
        os.system("umount {}".format(pth))

        MountManager.wait_mount(pth, umount=True)
        log.debug("Directory {} umounted".format(pth))

        shutil.rmtree(pth)


    def get_mountpoints(self) -> list[MountPoint]:
        """
        Return mounted filesystems
        """
        p = []
        for mpt in self._mountstore.values():
            p += list(mpt.get_partitions())
        return p


    def get_mountpoint(self, img:str) -> MountPoint|None:
        """
        Return a mount point
        """
        return self._mountstore.get(img)

    def get_image_path(self, mpt:str) -> str|None:
        """
        Get a mounted image location from the existing mountpoint
        """
        for i, m in self._mountstore.items():
            for p in m.get_partitions():
                if mpt == p:
                    return i


    def flush(self):
        """
        Flush all mounts entirely.
        """
        log.debug("Flushing mountpoints")
        for mpt in self.get_mountpoints():
            log.debug("Unmounting partition at {}".format(mpt))
            self.umount(mpt)
