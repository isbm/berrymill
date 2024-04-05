# Finds mountable images in specified locations
from __future__ import annotations

from collections import OrderedDict
import urllib
import kiwi.logger  # type: ignore
import os

log = kiwi.logging.getLogger("kiwi")
log.set_color_format()


class ImagePtr:
    """
    Image pointer that holds image type and its URI path
    """

    # Partitioned disk (bootloader, extended partitions, more rootfses etc)
    DISK_IMAGE = 0

    # Single image (KIS, container, rootfs etc)
    PARTITION_IMAGE = 1

    def __init__(self, fs_scheme: str, fs_path: str, fs_type: int):
        self.scheme: str = fs_scheme
        self.path: str = fs_path
        self.loop: str = ""  # Loop path

        assert fs_type in [self.DISK_IMAGE, self.PARTITION_IMAGE], "Unknown image type"
        self.img_type: int = fs_type

    def __repr__(self) -> str:
        return "<{}, type of {} for {} at {}>".format(self.__class__.__name__, self.scheme, self.path, hex(id(self)))


class ImageFinder:
    SCHEMES: list[str] = ["dir", "oci"]

    def __init__(self, *loc) -> None:
        """
        ImageFinder takes array of locations where images are.
        """
        self._i_pth = loc
        self._i_imgs: list[ImagePtr] = self._find_images()

    def __get_file_meta(self, p) -> str:
        """
        Get file meta
        """
        with os.popen("file {}".format(p)) as fp:
            return " ".join(list(filter(None, fp.read().split("\n")))).lower()

    def _is_qemu(self, p) -> bool:
        """
        Return True if a given filename is a QEMU disk image
        """
        meta = self.__get_file_meta(p)
        return " qemu " in meta and " image " in meta

    def _is_filesystem(self, p) -> bool:
        """
        Return True if a given filename is a mountable filesystem
        """
        return "filesystem" in self.__get_file_meta(p).lower()

    def _is_disk(self, p) -> bool:
        """
        Returns True if a given filename is a partitioned disk image
        """
        meta = self.__get_file_meta(p)
        return ("partition" in meta and "sector" in meta and "startsector" in meta) or "dos/mbr boot sector" in meta

    def _find_images(self) -> list[ImagePtr]:
        """
        Find images with filesystems
        """
        out: list[ImagePtr] = []
        for p in self._i_pth:
            log.debug("Looking for images in {}".format(p))
            if not "://" in p:
                raise Exception('Invalid url: "{}"'.format(p))
            upr: urllib.parse.ParseResult = urllib.parse.urlparse(p)
            assert upr.scheme in self.SCHEMES, "Unknown scheme in URL: {}".format(p)

            imgp: str = ""
            if upr.netloc:
                imgp = "./{}".format(upr.netloc) + upr.path  # Relative
            else:
                imgp = upr.path  # Absolute

            for f in os.listdir(imgp):
                f = os.path.join(imgp, f)
                if f.split(".")[-1].lower() not in ["qcow2", "raw"]:
                    continue  # Skip possible junk
                if self._is_filesystem(f):
                    out.append(ImagePtr(upr.scheme, f, ImagePtr.PARTITION_IMAGE))
                elif self._is_disk(f):
                    out.append(ImagePtr(upr.scheme, f, ImagePtr.DISK_IMAGE))
                elif self._is_qemu(f):
                    log.warn(f"{f} is a QEMU image")
                    log.warn(
                        "Currently QEMU images direct mount is not supported. Please convert it to RAW format using 'qemu-image' utility."
                    )
                else:
                    log.warning(f"Undetected image: {f}")
        return out

    def get_images(self) -> list[ImagePtr]:
        """
        Get found images
        """
        return self._i_imgs
