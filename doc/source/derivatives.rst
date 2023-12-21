Derived Images
==============

.. note::
   This chapter addresses derived images—images that share a common base but cater to distinct use cases and configurations.

Base Image
----------

Typically, when working with Kiwi NG, the project directory tree has a similar structure:

.. code-block:: shell

    ├─ description.kiwi
    ├─ config.sh
    └─ /root
       ├── /etc
       ├── /boot
       └── /usr/bin

Therefore there are three main components:

1. ``description.kiwi`` XML file. This is the main XML content description, which specifies all the setup, such as disk layout/size, partitions, packages, boot loader type etc.
2. ``config.sh`` script file. This is the main "hook" script, which contains all the necessary image customisations, those are applied as a final changes.
3. ``root`` overlay directory. Its content above is only an example. All files in this directory will be copied "as is" over the ``/`` (root) on the future provisioned filesystem.

There are few more optional script hooks available:

``post_bootstrap.sh``
    Runs in the final phase of bootstrap. It can be used to setup the package manager for subsequent chroot-based installation or similar tasks.

``images.sh``
    Is called at the beginning of the image creation process.

``disk.sh``
    Is invoked on an already generated image, is employed to implement alterations external to the root tree. It manages changes such as those pertaining to the partition table, contents of the final initrd, the bootloader, and similar elements.

``pre_disk_sync.sh``
    Same as ``disk.sh``, but called before the synchronisation of the root tree into the disk image loop file.

If ``delta_root`` is set to ``true``, Berrymill will also pick up the following scripts:

``config-overlay.sh``
    Is executed towards the conclusion of the preparation step, preceding the unmounting of the overlay root tree. Its execution follows that of ``config.sh``.

``config-host-overlay.sh``
    Same as ``config-overlay.sh``, except is running in **not chrooted** environment.

For more detailed information and even more possible scripts, please refer to the `shell scripts documentation <http://osinside.github.io/kiwi/concept_and_workflow/shell_scripts.html>`_ of Kiwi NG project.


Derivative
----------

Derived images are following concept of "subclass" in OOP programming languages: one can have different content descriptions, each one based on a previous. For example, ``description.kiwi`` is a base image, but e.g. ``emacs.kiwi`` is only adding another set of packages on top of the base description and so on. If you are familiar how Open Build Service works, it following the same concept of building a project on top of a parent project, which is built on top of a parent project etc.

Descriptions
^^^^^^^^^^^^

TBD

Scripts, Overlays and Configuration
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

Currently Berrymill does not provide any framework with regard of deriving configuration scripts, because it is not very necessary. It can be done on your own just organising shell commands in a separate functions as a library and then including these snippets into your ``config.sh`` or any other hook.
