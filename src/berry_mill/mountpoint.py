# Mountpoint collects all mountpoints into one database
# and is globally available as a singleton.
# Plugins and other operations can refer there at any time
# for arbitrary whatever operations they do.
#
# Teardown (unmount) happens at the end of Berrymill cycle.

from __future__ import annotations
from collections import OrderedDict
from typing import Any, Callable
import kiwi.logger  # type: ignore
import time
import os
import tempfile
import shutil
from berry_mill.imagefinder import ImagePtr


log = kiwi.logging.getLogger("kiwi")
log.set_color_format()  # ddd


class MountData:
    """
    Mount data (basically just a parsed output of "mount" command)
    """

    def __init__(self) -> None:
        self.__mount_data: list[list[str]] = []
        for l in [x.strip() for x in os.popen("mount").read().split(os.linesep)]:
            tk: list[str] = l.split(" ")
            if len(tk) == 6:
                self.__mount_data.append([x for x in tk if x not in ["on", "type"]])

    @staticmethod
    def update_mount_data(m) -> Callable[..., Any]:
        """
        Update mount data
        """

        def w(self, *args, **kw) -> Any:
            if self._mount_data is None:
                self._mount_data = MountData()
            return m(self, *args, **kw)

        return w

    @staticmethod
    def _a2t(attrs: str) -> list[str]:
        return attrs[1 : len(attrs) - 1].split(",")

    def get_attrs_by_dev(self, device: str) -> tuple[str, ...] | tuple[()]:
        """
        Return attributes of a mountpoint by device
        """
        for md in self.__mount_data:
            dev, _, _, attrs = md
            if dev == device:
                return tuple(MountData._a2t(attrs))
        return ()

    def get_attrs_by_mpt(self, mountpoint: str) -> tuple[str, ...] | tuple[()]:
        """
        Return attributes of a mountpoint by its location directory
        """
        for md in self.__mount_data:
            _, mpt, _, attrs = md
            if mpt == mountpoint:
                return tuple(MountData._a2t(attrs))
        return ()


class MountPoint:
    """
    MountPoint holds all the information about an object,
    whether it is a single simple image or a partitioned disk device.
    """

    def __init__(self) -> None:
        self._partitions: set[str] = set()
        self._loop_devices: dict[str, str] = {}

    def add(self, pth: str, loopdev: str) -> MountPoint:
        self._partitions.add(pth)
        self._loop_devices[pth] = loopdev
        return self

    def get_partitions(self) -> tuple[str, ...]:
        """
        Return mounted partitions
        """
        return tuple(self._partitions)

    def get_loop_device(self, pth: str) -> str | None:
        return self._loop_devices.get(pth)

    def get_loop_devices(self) -> tuple[str, ...]:
        """
        Return loop devices
        """
        return tuple(self._loop_devices.values())


class MountManager:
    """
    MountManager is an in-memory store of all mounted devices.
    Can be imported and instantiated from anywhere
    """

    _instance: MountManager | None = None
    _mountstore: OrderedDict
    _mount_data: MountData | None = None

    def __new__(cls) -> MountManager:
        if cls._instance is None:
            cls._instance = super(MountManager, cls).__new__(cls)
            cls._instance._mountstore = OrderedDict()
        return cls._instance

    @staticmethod
    def wait_mount(dst: str, umount: bool = False):
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

    def __mount_partition_image(self, img_ptr: ImagePtr) -> MountPoint:
        """
        Mount a single partition image, return mounted directory
        """

        mpt: MountPoint | None = self.get_mountpoint(img_ptr.path)
        if mpt is not None:
            return mpt

        dst: str = tempfile.TemporaryDirectory(prefix="bml-{}-mnt-".format(os.path.basename(img_ptr.path))).name
        os.makedirs(dst)

        mpt = MountPoint()
        img_ptr.loop = os.popen("losetup --show -Pf {}".format(img_ptr.path)).read().strip()

        log.debug("Mounting {} as a loop device ({}) to {}".format(img_ptr.path, img_ptr.loop, dst))
        os.system("mount {} {}".format(img_ptr.loop, dst))

        MountManager.wait_mount(dst)

        log.debug("Device {} has been mounted successfully".format(img_ptr.loop))
        self._mountstore[img_ptr] = mpt.add(dst, img_ptr.loop)

        return mpt

    def __mount_disk_image(self, img_ptr: ImagePtr) -> None:
        """
        Mount a partitioned disk image
        """
        # Get a list of partitions
        log.debug("Mounting disk image at {}".format(img_ptr.path))

        # Setup loops
        mpt = MountPoint()
        img_ptr.loop = os.popen("losetup --show -Pf {}".format(img_ptr.path)).read().strip()

        loop_devices: list[str] = []
        # Get all other loop devs
        for dev in os.listdir("/dev"):
            dev = "/dev/{}".format(dev)
            if dev.startswith(img_ptr.loop) and dev != img_ptr.loop:
                log.debug("Registering loop device {}".format(dev))
                loop_devices.append(dev)

        # Mount each partition/loop to its own target
        pt: int = 1
        for dev in loop_devices:
            dst: str = tempfile.TemporaryDirectory(
                prefix="bml-{}-mnt_pt-{}_dev-{}".format(os.path.basename(img_ptr.path), pt, os.path.basename(dev))
            ).name
            os.makedirs(dst)
            log.debug("Mounting {} partition {} as a loop device ({}) to {}".format(img_ptr.path, pt, dev, dst))
            os.system("mount {} {}".format(dev, dst))
            log.debug("Device {} has been mounted successfully".format(dev))
            mpt.add(dst, dev)
            pt += 1
        self._mountstore[img_ptr] = mpt

    def mount(self, img_ptr: ImagePtr) -> None:
        """
        Mount a specific path to a tempdir. If `dst` is not given,
        temporary directory is returned.

        If mount fails, exception is raised.
        """

        if img_ptr.img_type == ImagePtr.PARTITION_IMAGE:
            self.__mount_partition_image(img_ptr)
            return
        elif img_ptr.img_type == ImagePtr.DISK_IMAGE:
            self.__mount_disk_image(img_ptr)
            return

        raise Exception("Unable to mount image: {}".format(repr(img_ptr)))

    def umount(self, pth: str) -> None:
        """
        Un-mount a specific path and cleanup everything.
        Exception is raised on failure
        """
        log.debug("Umounting {}".format(pth))
        os.system("umount {} 2>/dev/null".format(pth))

        MountManager.wait_mount(pth, umount=True)
        log.debug("Directory {} umounted".format(pth))

        shutil.rmtree(pth)

    @MountData.update_mount_data
    def get_mountpoints(self) -> list[str]:
        """
        Return mounted filesystems
        """
        p = []
        for mpt in self._mountstore.values():
            p += list(mpt.get_partitions())
        return p

    @MountData.update_mount_data
    def get_loop_devices(self) -> list[str]:
        d = []
        for mpt in self._mountstore.values():
            d += list(mpt.get_loop_devices())
        return d

    @MountData.update_mount_data
    def get_loop_device_by_mountpoint(self, mpt: str) -> str | None:
        for i, m in self._mountstore.items():
            dev = m.get_loop_device(mpt)
            if dev is not None:
                return dev
        return None

    @MountData.update_mount_data
    def get_mountpoint(self, img: str) -> MountPoint | None:
        """
        Return a mount point
        """
        return self._mountstore.get(img)

    @MountData.update_mount_data
    def get_image_path(self, mpt: str) -> str | None:
        """
        Get a mounted image location from the existing mountpoint
        """
        for i, m in self._mountstore.items():
            for p in m.get_partitions():
                if mpt == p:
                    return i.path
        return None

    @MountData.update_mount_data
    def is_writable(self, mountpoint: str) -> bool:
        """
        Return True is a mountpoint is writable.
        """
        assert self._mount_data is not None, "Mount data wasnt updated"
        attrs: tuple[str, ...] | tuple[()] = self._mount_data.get_attrs_by_mpt(mountpoint=mountpoint)
        return "rw" in attrs and "ro" not in attrs

    @MountData.update_mount_data
    def get_partition_mountpoint_by_ord(self, num: int) -> str | None:
        """
        Get partition mountpoint by its order.

        :param pth (str): Configured path where built images are searched, assuming one image per a path
        :param num (int): Partition number
        """
        for img_ptr, mpt in self._mountstore.items():
            for pdir in mpt.get_partitions():
                if num == int(os.path.basename(mpt.get_loop_device(pdir))[4:].split("p")[-1]):
                    return pdir
        return None

    def flush(self):
        """
        Flush all mounts entirely.
        """
        log.debug("Flushing mountpoints")
        for mpt in self.get_mountpoints():
            self.umount(mpt)

        root_loopdev: str | None = None
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

        self._mount_data = None
