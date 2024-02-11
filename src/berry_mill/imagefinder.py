# Finds mountable images in specified locations
import urllib
import kiwi.logger
import os


log = kiwi.logging.getLogger('kiwi')
log.set_color_format()


class ImagePtr:
    """
    Image pointer that holds image type and its URI path
    """
    def __init__(self, fs_scheme, fs_path):
        self.scheme = fs_scheme
        self.path = fs_path

    def __repr__(self) -> str:
        return "<{}, type of {} for {} at {}>".format(self.__class__.__name__, self.scheme, self.path, hex(id(self)))


class ImageFinder:
    SCHEMES:list[str] = ["dir", "oci"]

    def __init__(self, *loc) -> None:
        """
        ImageFinder takes array of locations where images are.
        """
        self._i_pth = loc
        self._i_imgs:list[ImagePtr] = self._find_images()

    def _is_filesystem(self, p) -> bool:
        """
        Return True if a given filename is a mountable filesystem
        """
        out:str = ""
        with os.popen("file {}".format(p)) as fp:
            out = " ".join(list(filter(None, fp.read().split("\n"))))

        return "filesystem" in out.lower()

    def _find_images(self) -> list[ImagePtr]:
        """
        Find images with filesystems
        """
        out:list[str] = []
        for p in self._i_pth:
            log.debug("Looking for images in {}".format(p))
            if not "://" in p:
                raise Exception("Invalid url: \"{}\"".format(p))
            upr:urllib.parse.ParseResult = urllib.parse.urlparse(p)
            assert upr.scheme in self.SCHEMES, "Unknown scheme in URL: {}".format(p)

            imgp:str = ""
            if upr.netloc:
                imgp = "./{}".format(upr.netloc) + upr.path # Relative
            else:
                imgp = upr.path # Absolute

            for f in os.listdir(imgp):
                f = os.path.join(imgp, f)
                if self._is_filesystem(f):
                    out.append(ImagePtr(upr.scheme, f))
        return out

    def get_images(self) -> list[ImagePtr]:
        """
        Get found images
        """
        return tuple(self._i_imgs)
