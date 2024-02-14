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
        self._loop_devices:list[str, str] = {}

    def add(self, pth:str, loopdev:str) -> MountPoint:
        self._partitions.add(pth)
        self._loop_devices[pth] = loopdev
        return self

    def get_partitions(self) -> list[str]:
        """
        Return mounted partitions
        """
        return tuple(self._partitions)

    def get_loop_device(self, pth:str) -> str|None:
        return self._loop_devices.get(pth)

    def get_loop_devices(self) -> list[str]:
        """
        Return loop devices
        """
        return tuple(self._loop_devices.values())

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


    def __mount_partition_image(self, img_ptr:ImagePtr) -> str:
        """
        Mount a single partition image, return mounted directory
        """

        mpt = self.get_mountpoint(img_ptr.path)
        if mpt:
            return mpt

        dst:str = tempfile.TemporaryDirectory(prefix="bml-{}-mnt-".format(os.path.basename(img_ptr.path))).name
        os.makedirs(dst)

        mpt = MountPoint()
        loopdev = os.popen("losetup --show -Pf {}".format(img_ptr.path)).read().strip()

        log.debug("Mounting {} as a loop device ({}) to {}".format(img_ptr.path, loopdev, dst))
        os.system("mount {} {}".format(loopdev, dst))

        MountManager.wait_mount(dst)

        log.debug("Device {} has been mounted successfully".format(loopdev))
        self._mountstore[img_ptr] = mpt.add(dst, loopdev)

        return dst

    def __mount_disk_image(self, img_ptr:ImagePtr) -> None:
        """
        Mount a partitioned disk image
        """
        # Get a list of partitions
        log.debug("Mounting disk image at {}".format(img_ptr.path))

        # Setup loops
        mpt = MountPoint()
        main_loop_dev = os.popen("losetup --show -Pf {}".format(img_ptr.path)).read().strip()

        loop_devices:list[str] = []
        # Get all other loop devs
        for dev in os.listdir("/dev"):
            dev = "/dev/{}".format(dev)
            if dev.startswith(main_loop_dev) and dev != main_loop_dev:
                log.debug("Registering loop device {}".format(dev))
                loop_devices.append(dev)

        # Mount each partition/loop to its own target
        pt:int = 1
        for dev in loop_devices:
            dst:str = tempfile.TemporaryDirectory(prefix="bml-{}-mnt_pt-{}_dev-{}".format(os.path.basename(img_ptr.path), pt, os.path.basename(dev))).name
            os.makedirs(dst)
            log.debug("Mounting {} partition {} as a loop device ({}) to {}".format(img_ptr.path, pt, dev, dst))
            os.system("mount {} {}".format(dev, dst))
            log.debug("Device {} has been mounted successfully".format(dev))
            mpt.add(dst, dev)
            pt += 1
        self._mountstore[img_ptr] = mpt

    def mount(self, img_ptr:ImagePtr) -> str:
        """
        Mount a specific path to a tempdir. If `dst` is not given,
        temporary directory is returned.

        If mount fails, exception is raised.
        """

        if img_ptr.img_type == ImagePtr.PARTITION_IMAGE:
            return self.__mount_partition_image(img_ptr)
        elif img_ptr.img_type == ImagePtr.DISK_IMAGE:
            return self.__mount_disk_image(img_ptr)

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


    def get_mountpoints(self) -> list[str]:
        """
        Return mounted filesystems
        """
        p = []
        for mpt in self._mountstore.values():
            p += list(mpt.get_partitions())
        return p

    def get_loop_devices(self) -> list[str]:
        d = []
        for mpt in self._mountstore.values():
            d += list(mpt.get_loop_devices())
        return d

    def get_loop_device_by_mountpoint(self, mpt:str) -> str|None:
        for i, m in self._mountstore.items():
            dev = m.get_loop_device(mpt)
            if dev is not None:
                return dev

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
                    return i.path


    def flush(self):
        """
        Flush all mounts entirely.
        """
        log.debug("Flushing mountpoints")
        for mpt in self.get_mountpoints():
            log.debug("Unmounting partition at {}".format(mpt))
            self.umount(mpt)

        root_loopdev:str|None = None
        for loopdev in self.get_loop_devices():
            l = os.path.basename(loopdev)[4:]
            if "p" in l:
                root_loopdev = l.split("p")[0]
            else:
                root_loopdev = l
            break

        root_loopdev = "/dev/loop{}".format(root_loopdev)
        log.debug("Detaching {} device".format(root_loopdev))
        os.system("losetup -d {}".format(root_loopdev))
