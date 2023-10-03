from __future__ import annotations

from typing import List, Set
from typing import TypedDict
from typing_extensions import Unpack
from lxml import etree
import os
import sys
import shutil
import tempfile
import requests
import inquirer
import re
import subprocess

from urllib.parse import ParseResult, urlparse, quote, urljoin
from typing import Dict
from berry_mill.kiwiapp import KiwiAppLocal, KiwiAppBox
from kiwi.kiwi import KiwiError
from platform import machine

class KiwiParams(TypedDict):
    """
    Dictionary for Kiwi Parameters

    Attributes:

        profile (str, Optional): select profile for images that makes use of it.
        box_memory (str, Default: 8G): specify main memory to use for the QEMU VM (box).
        debug (bool, Default: False): run in debug mode. This means the box VM stays open and the kiwi log level is set to debug(10).
        clean (bool, Default: False): cleanup previous build results prior build.
        cross (bool, Default: False): cross image build on x86_64 to aarch64 target.
        cpu (str, Optional): cpu to use for the QEMU VM (box)
        local (bool, Default: False): run build process locally on this machine. Requires sudo setup and installed KIWI toolchain.
        target_dir (str, Default:/tmp/IMAGE_NAME[.PROFILE_NAME]): store image results in given dirpath.
    """
    profile: str
    box_memory: str
    debug: bool
    clean: bool
    cross: bool
    cpu: str
    local: bool
    target_dir: str


class KiwiBuilder:
    """
    Kiwi wrapper for appliance builder.
    """
    # TODO handle TypeError
    def __init__(self, descr:str, **kw: Unpack[KiwiParams]):
        self._repos:Dict[str, Dict[str, str]] = {}
        self._appliance_path:str = os.getcwd()
        print(self._appliance_path)
        self._appliance_descr:str = descr
        self._params:Dict[KiwiParams] = kw

        if self._params.get("target_dir"):
            self._params["target_dir"] = self._params["target_dir"].rstrip("/")

        self._trusted_gpg_d:str = "/etc/apt/trusted.gpg.d"
        self._release_gpg_filename: str = 'Release.gpg'
        self._release_ref_filename: str = 'Release'
        self._tmpdir:str = tempfile.mkdtemp(prefix="berrymill-keys-", dir="/tmp")

        self._boxrootdir:str = os.path.join(self._appliance_path, "boxroot")
        print(self._boxrootdir)
        self._fcleanbox:bool = False
        # tmp boxroot dir only needed when build mode is not local
        if not self._params.get("local", False):
            boxdir:str = os.path.join(self._appliance_path, "boxroot")
            if not os.path.exists(boxdir):
                # flag for cleanup to remember to also delete boxroot dir if
                # it hasnt existed before already
                self._fcleanbox = True
                os.makedirs(boxdir)

            self._boxtmpkeydir:str = tempfile.mkdtemp(prefix="berrymill-keys-", dir= self._boxrootdir)

            self._boxtmpargdir:str = tempfile.mkdtemp(prefix="berrymill-args-", dir= self._boxrootdir)

    def add_repo(self, reponame:str, repodata:Dict[str, str]) -> KiwiBuilder:
        """
        Add a repository for the builder
        """
        if reponame:
            repodata["key"] = "file://" + self._get_repokeys(reponame, repodata)
            self._check_repokey(repodata, reponame)
            self._repos[reponame] = repodata
        else:
            print("Repository name not defined")
            sys.exit(1)

        return self

    def _import_repokey(self, url: str, reponame: str, g_path: str) -> None:
        """
        Extract repository keys ID and download pub key from ubuntu keyserver
        """
        try:
            # Create temporary files for Release.gpg and Release
            with tempfile.NamedTemporaryFile(dir=self._tmpdir, delete=False) as temp_release_gpg:
                temp_release_gpg.write(requests.get(f"{url}/Release.gpg", allow_redirects=True).content)
                temp_release_gpg_path: str = temp_release_gpg.name

            with tempfile.NamedTemporaryFile(dir=self._tmpdir, delete=False) as temp_release:
                temp_release.write(requests.get(f"{url}/Release", allow_redirects=True).content)
                temp_release_path: str = temp_release.name

            # Extract Key ID
            command: str = f'gpg --keyid-format long --verify {temp_release_gpg_path}  {temp_release_path}'
            result: subprocess.CompletedProcess[str] = subprocess.run(command, shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)
            key_id_pattern: str = r'using \w+ key ([0-9A-F]+)'
            key_match: str = re.search(key_id_pattern, str(result))

            if key_match:
                key_id: str = key_match.group(1)
                # Download Key
                url_k: str = f'http://keyserver.ubuntu.com/pks/lookup?op=get&search=0x{key_id}'
                response: requests.Response = requests.get(url_k, allow_redirects=True)
                with open(g_path, "wb") as f_rel:
                    f_rel.write(response.content)
            else:
                print(f"Error: Failed to extract Key ID from '{reponame}'")

        except requests.RequestException as req_err:
            print(f"Request error: {req_err}")
        except subprocess.CalledProcessError as cmd_err:
            print(f"Command execution error: {cmd_err}")
        except Exception as e:
            print(f"An error occurred: {e}")

    def _get_repokeys(self, reponame: str, repodata:Dict[str, str]) -> str:
        """
        Download repository keys to a temporary directory
        """
        # Check if repo name and date are defined
        for repo_iter, excep_iter in [(repodata, "Repository data not defined"),
                             (reponame, "Repository name not defined"),
                             (repodata.get('url'), "URL not found")]:
            if not repo_iter:
                raise Exception(excep_iter)

        url: ParseResult = urlparse(repodata["url"])
        g_path:str = os.path.join(self._tmpdir, f"{reponame}_release.key")

        if repodata.get("components", "/") != "/":
            s_url = urljoin(f"{url.scheme}://{url.netloc}/{url.path}/dists/{repodata['name']}", "")
            self._import_repokey(s_url, reponame, g_path)
            return g_path
        else:
            s_url: str = os.path.join(url.scheme + "://" + url.netloc, url.path, 'Release.key')
            response = requests.get(s_url, allow_redirects=True)
            with open(g_path, "wb") as f_rel:
                f_rel.write(response.content)
            response.close()
            return g_path


    def _get_relative_file_uri(self, repo_key_path) -> str:
        """
        Change the file:// URIs in the repo key values to be relative to the boxroot
        """
        if not self._boxtmpkeydir:
            raise Exception("Key directory not available")
        if not repo_key_path:
            raise Exception("Key path not defined")
        return "file:///" + \
               quote( \
               os.path.join( \
               os.path.basename(self._boxtmpkeydir), os.path.basename(repo_key_path)))

    def _check_repokey(self, repodata:Dict[str, str], reponame) -> None:
        if not repodata.get("key"):
            raise Exception("Path to the key is not defined")
        parsed_url = urlparse(repodata.get("key"))
        if not parsed_url.path:
            print("Berrymill was not able to retrieve a fitting gpg key")
            if os.path.exists(self._trusted_gpg_d):
                keylist:List[str] = os.listdir(self._trusted_gpg_d)
                selected = self._key_selection(reponame, keylist)
                if selected:
                    repodata["key"] = ParseResult(scheme="file",
                                                path=os.path.join(self._trusted_gpg_d, selected),
                                                params=None, query=None, fragment=None,
                                                netloc=None).geturl()
                    self._check_repokey(repodata, reponame)
                    return
            else:
                print("Trusted key not foud on system")
        if not os.path.exists(parsed_url.path):
            self._cleanup()
            Exception(parsed_url.path + " does not exist" if parsed_url.path else f"key file path not specified for {reponame}")

    def _write_repokeys_box(self, repos:Dict[str, Dict[str, str]]) -> None:
        """
        Write repo keys from the self._tmp dir to the boxroot, so kiwi box can access the keys
        It expects a file:// uri to be present in repos[reponame][key]
        """
        dst = self._boxtmpkeydir
        if not dst:
            raise Exception("ERROR: Boxroot directory is not defined")

        for reponame in repos:
            k = repos.get(reponame, {}).get("key")
            parsed_url = urlparse(k)
            try:
                shutil.copy(parsed_url.path, dst)
            except Exception as exc:
                print(f"ERROR: Failure while trying to copying the keyfile at {parsed_url.path}")
                print(exc)
                self._cleanup()
                sys.exit(1)
            repos.get(reponame, {})["key"] = self._get_relative_file_uri(parsed_url.path)


    def _cleanup(self) -> None:
        """
        Cleanup the environment after the build
        """
        print("Cleaning up...")
        try:
            shutil.rmtree(self._tmpdir)
            if not self._params.get("local", False):
                shutil.rmtree(self._boxtmpkeydir)
                shutil.rmtree(self._boxtmpargdir)
                if self._fcleanbox:
                    # if Flag fcleanbox is true an empty boxroot is guranteed to exist
                    shutil.rmtree(os.path.join(self._appliance_path, "boxroot"))
        except Exception as e:
            print(f"Error: Cleanup Failed : {e}")

        print("Cleanup finished")

    def _key_selection(self, reponame:str, options:List[str]) -> str | None:
        none_of_above = "none of the above"
        question = [
        inquirer.List("choice",
                  message="Choose the right key for {}:".format(reponame),
                  choices=options + [none_of_above],
                  default=none_of_above,
                  carousel=True
                  ),
        ]
        answer = inquirer.prompt(question)
        print("You selected:", answer["choice"])

        return answer["choice"] != none_of_above and answer["choice"] or None


    def build(self) -> None:
        """
        Run builder. It supposed to be already within that directory (os.chdir).
        Directory is changed by the parent caller of the KiwiBuilder class.
        """
        print("Using appliance \"{}\" located at \"{}\"".format(self._appliance_descr, self._appliance_path))
        # options that are solely accepted by kiwi-ng
        kiwi_options = []
        # options, solely accepted by box-build plugin
        box_options:List[str] = ["--box","ubuntu"]

        if self._params.get("debug", False):
            kiwi_options.append("--debug")
            box_options.append("--box-debug")

        if self._params.get("cpu"):
            box_options = ["--cpu", self._params.get("cpu")] + box_options

        if self._params.get("box_memory"):
            box_options += ["--box-memory", self._params.get("box_memory")]

        if machine() == "aarch64":
            box_options += ["--machine", "virt"]

        # TODO: When using cross, e.g. cpu param needs to be disabled
        if self._params.get("cross") and machine() == "x86_64":
            box_options += ["--aarch64", "--cpu", "cortex-a57", "--machine", "virt", "--no-accel"]
            kiwi_options += ["--target-arch", "aarch64"]


        try:
            config_tree = etree.parse(f"{self._appliance_descr}")
        except Exception as err:
            print("ERROR: Failure {} while parsing appliance description".format(err))
            sys.exit(1)

        try:
            image_name:list = config_tree.xpath("//image/@name")
        except Exception as err:
            print("ERROR: Failure {} while trying to extract image name", err)
            sys.exit(1)

        target_dir = os.path.join(
            self._params.get("target_dir","/tmp"),\
            f"{image_name[0]}.{self._params.get('profile', '')}")

        profiles = config_tree.xpath("//profile/@name")

        if not self._params.get("profile") and profiles:
            print("No Profile selected.")
            print("Please select one of the available following profiles using --profile:")
            print(profiles)
            self._cleanup()
            sys.exit(1)

        if self._params.get("profile"):
            profile = self._params.get("profile")
            if profile in profiles:
                kiwi_options += ["--profile", profile]
            else:
                self._cleanup()
                raise Exception(f"\'{profile}\' is not a valid profile. Available: {profiles}")


        if self._params.get("clean", False):
            clean_target = target_dir
            if self._params.get("profile"):
                clean_target += f".{self._params.get('profile')}"
            if self._params.get("local", False):
                shutil.rmtree(clean_target)

        if not self._params.get("local", False):
            self._write_repokeys_box(self._repos)

        if self._params.get("local", False):
            command = ["kiwi-ng"] + kiwi_options\
                    + ["system", "build", "--description", "."]\
                    + ["--target-dir", target_dir] 

            try:
                print("Starting Kiwi for local build")                
                KiwiAppLocal(command, repos=self._repos).run()
            except KiwiError as kiwierr:
                print("KiwiError:", type(kiwierr).__name__)
                print(kiwierr)
                self._cleanup()
                sys.exit(1)
        else:
            command = ["kiwi-ng"]+ kiwi_options\
                    + ["system", "boxbuild"] + box_options\
                    + ["--", "--description", '.'] + ["--target-dir", target_dir]\

            try:
                print("Starting Kiwi Box")
                KiwiAppBox(command, repos=self._repos, args_tmp_dir=self._boxtmpargdir).run()
            except KiwiError as kiwierr:
                print("KiwiError:", type(kiwierr).__name__)
                print(kiwierr)
                self._cleanup()
                sys.exit(1)

        # run kiwi here with "appliance_init" which is a ".kiwi" file
        os.system("ls -lah")

        print(self._repos)

        self._cleanup()
