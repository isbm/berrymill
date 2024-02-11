# Mountpoint collects all mountpoints into one database
# and is globally available as a singleton.
# Plugins and other operations can refer there at any time
# for arbitrary whatever operations they do.
#
# Teardown (unmount) happens at the end of Berrymill cycle.

from collections import OrderedDict
import kiwi.logger
import time
import os
import tempfile
import shutil

log = kiwi.logging.getLogger('kiwi')
log.set_color_format()


class _MountPointMeta(type):
    """
    Singleton metaclass
    """
    def __init__(cls, name, bases, class_dict):
        super(_MountPointMeta, cls).__init__(name, bases, class_dict)

        o_new = cls.__new__

        def s_new(cls, *a, **kw):
            if cls._instance == None:
                cls._instance = o_new(cls,*a,**kw)
            return cls._instance

        cls._instance = None
        cls.__new__ = staticmethod(s_new)


class MountPoint(metaclass=_MountPointMeta):
    """
    MountPoint in-memory store of all mounted devices.
    Can be imported and instantiated from anywhere
    """
    def __init__(self) -> None:
        self._mountstore:OrderedDict[str, str] = OrderedDict()

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
            dst = tempfile.TemporaryDirectory(prefix="bml-sbom-").name
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
        return self._mountstore.keys()


    def get_mountpoint(self, mpt:str) -> str|None:
        """
        Return a mount point
        """
        return self._mountstore.get(mpt)


    def flush(self):
        """
        Flush all mounts entirely.
        """
        [self.umount(pth) for pth in self._mountstore.values()]
