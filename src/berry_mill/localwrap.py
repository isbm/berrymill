from typing import Dict
from kiwi.tasks.system_build import SystemBuildTask

import os
import logging
from itertools import zip_longest

# project
from kiwi.help import Help
from kiwi.system.prepare import SystemPrepare
from kiwi.system.setup import SystemSetup
from kiwi.builder import ImageBuilder
from kiwi.system.profile import Profile
from kiwi.defaults import Defaults
from kiwi.privileges import Privileges
from kiwi.path import Path

log = logging.getLogger('kiwi')



class WrapperSystemBuildTask(SystemBuildTask):
    """
    """
    def run(self, repos:Dict[str, Dict[str,str]]):
        """
        Build a system image from the specified description. The
        build command combines the prepare and create commands
        """
        # NOTE: mainly copied from parent class!!
        self.manual = Help()
        if self._help():
            return

        Privileges.check_for_root_permissions()

        abs_target_dir_path = os.path.abspath(
            self.command_args['--target-dir']
        )
        build_dir = os.sep.join([abs_target_dir_path, 'build'])
        image_root = os.sep.join([build_dir, 'image-root'])
        Path.create(build_dir)

        if not self.global_args['--logfile']:
            log.set_logfile(
                os.sep.join([abs_target_dir_path, 'build', 'image-root.log'])
            )

        self.load_xml_description(
            self.command_args['--description'], self.global_args['--kiwi-file']
        )

        build_checks = self.checks_before_command_args
        build_checks.update(
            {
                'check_target_directory_not_in_shared_cache':
                    [abs_target_dir_path]
            }
        )
        self.run_checks(build_checks)

        if self.command_args['--ignore-repos']:
            self.xml_state.delete_repository_sections()
        elif self.command_args['--ignore-repos-used-for-build']:
            self.xml_state.delete_repository_sections_used_for_build()

        if self.command_args['--set-repo']:
            self.xml_state.set_repository(
                *self._get_repo_parameters(
                    self.command_args['--set-repo'],
                    self.command_args['--set-repo-credentials']
                )
            )
        
        # injected code
        #-------------------------------------------------------------------
        self.xml_state.delete_repository_sections()
        for reponame in repos:

            repodata:Dict[str,str] = repos.get(reponame)

            components = repodata.get("components", "/")
            components = components if components != '/' else None

            distro = repodata.get("name", None)
            print(repodata.get("key"))
            self.xml_state.add_repository(
                repo_source=repodata.get("url"),
                repo_type=repodata.get("type"),
                repo_alias=reponame,
                repo_signing_keys=[repodata.get("key")],
                components=components,
                distribution=distro,
                repo_gpgcheck=False
            )
        #----------------------------------------------------------------------
        if self.command_args['--add-repo']:
            for add_repo, add_credentials in zip_longest(
                self.command_args['--add-repo'],
                self.command_args['--add-repo-credentials']
            ):
                self.xml_state.add_repository(
                    *self._get_repo_parameters(add_repo, add_credentials)
                )

        if self.command_args['--set-container-tag']:
            self.xml_state.set_container_config_tag(
                self.command_args['--set-container-tag']
            )

        if self.command_args['--add-container-label']:
            for add_label in self.command_args['--add-container-label']:
                try:
                    (name, value) = add_label.split('=', 1)
                    self.xml_state.add_container_config_label(name, value)
                except Exception:
                    log.warning(
                        'Container label {0} ignored. Invalid format: '
                        'expected labelname=value'.format(add_label)
                    )

        if self.command_args['--set-container-derived-from']:
            self.xml_state.set_derived_from_image_uri(
                self.command_args['--set-container-derived-from']
            )

        self.run_checks(self.checks_after_command_args)

        log.info('Preparing new root system')
        system = SystemPrepare(
            self.xml_state,
            image_root,
            self.command_args['--allow-existing-root']
        )
        manager = system.setup_repositories(
            self.command_args['--clear-cache'],
            self.command_args[
                '--signing-key'
            ] + self.xml_state.get_repositories_signing_keys(),
            self.global_args['--target-arch']
        )
        system.install_bootstrap(
            manager, self.command_args['--add-bootstrap-package']
        )

        setup = SystemSetup(
            self.xml_state, image_root
        )
        setup.import_description()

        # call post_bootstrap.sh script if present
        setup.call_post_bootstrap_script()

        system.install_system(
            manager
        )
        if self.command_args['--add-package']:
            system.install_packages(
                manager, self.command_args['--add-package']
            )
        if self.command_args['--delete-package']:
            system.delete_packages(
                manager, self.command_args['--delete-package']
            )

        profile = Profile(self.xml_state)

        defaults = Defaults()
        defaults.to_profile(profile)
        profile.create(
            Defaults.get_profile_file(image_root)
        )

        setup.import_overlay_files()
        setup.import_image_identifier()
        setup.setup_groups()
        setup.setup_users()
        setup.setup_keyboard_map()
        setup.setup_locale()
        setup.setup_plymouth_splash()
        setup.setup_timezone()
        setup.setup_permissions()
        setup.setup_selinux_file_contexts()

        # make sure manager instance is cleaned up now
        del manager

        # setup permanent image repositories after cleanup
        setup.import_repositories_marked_as_imageinclude()

        # call config.sh script if present
        setup.call_config_script()

        # handle uninstall package requests, gracefully uninstall
        # with dependency cleanup
        system.pinch_system(force=False)

        # handle delete package requests, forced uninstall without
        # any dependency resolution
        system.pinch_system(force=True)

        # delete any custom rpm macros created
        system.clean_package_manager_leftovers()

        # make sure system instance is cleaned up now
        del system

        setup.call_image_script()

        # make sure setup instance is cleaned up now
        del setup

        log.info('Creating system image')
        self.run_checks(
            {
                'check_dracut_module_versions_compatible_to_kiwi':
                    [image_root]
            }
        )
        image_builder = ImageBuilder.new(
            self.xml_state,
            abs_target_dir_path,
            image_root,
            custom_args={
                'signing_keys': self.command_args[
                    '--signing-key'
                ] + self.xml_state.get_repositories_signing_keys(),
                'xz_options': self.runtime_config.get_xz_options()
            }
        )
        result = image_builder.create()
        result.print_results()
        result.dump(
            os.sep.join([abs_target_dir_path, 'kiwi.result'])
        )