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

Berrymill is an appliance generator of root file systems, mostly used for embedded devices, but is not limited to this. The main purpose of it is to be a wrapper around Kiwi NG and allow to build images equally on
https://openbuildservice.org as well as locally, without any changes to the image content description.

It implements the concept of derived images extending Kiwi image descriptions with small derivations like adding or removing packages, changing the size or the type of a file system etc.

In order to derive an image, create a new image description XML file, e.g. ``emacs.kiwi`` and add ``inherit`` tag:

.. code-block:: xml

    <?xml version="1.0" encoding="utf-8"?>
    <image schemaversion="6.8" name="Best Editor">
        <inherit path="description.xml"/>
    </image>

Building an image using ``emacs.kiwi`` description instead of ``description.xml`` file is not that beneficial, because it will result into the same image. But at this point, ``emacs.kiwi`` simply duplicates everything what is specified in the derived description. You will need to "shadow" tags in the parent description by adding modifier tags to the ``emacs.kiwi`` so then it would make more sense. There are number of tags that allows to modify parent data.

``<add/>``
    Add specific data to the derived image like a package, or other elements. This tag does not need of XPath use, but will require "wrapping" a target group. So if you want to add another ``<package/>`` tag to the common list, you need to also make sure which group it belongs to. In this case, it belongs to a group ``<packages/>`` that has ``type="iso"``. Example usage:

.. code-block:: xml

        <add>
            <packages type="iso">
                <package name="emacs-nox"/>
            </packages>
        </add>

``<remove/>``
    Remove parts of the original image in the derived image, could be e.g., packages, aggregates... Example:

.. code-block:: xml

        <remove>
            <packages type="image">
                <package name="vim"/>
            </packages>
        </remove>

``<merge/>`` and ``<replace/>``
    Merge and replace only work on aggregates. One could for example, merge an additional `type` element to the `preferences`:

.. code-block:: xml

        <merge>
            <preferences>
                <type image="typename" primary="true"/>
            </preferences>
        </merge>

``<remove_any/>``
    Remove any element from description that matches by attributes at least. In contrast to `remove`, this does not need precise tag description. Instead it is considering attributes to narrow down what tags to remove from the description. For example, it is possible to use it to remove all users configured with plain password format:

.. code-block:: xml

        <remove_any>
            <user pwdformat="plain"/>
        </remove_any>

``<set/>``
    This operation is the only one that is using XPath to target an exact tag at precise point. It sets attributes on an element to add or update attributes on a specific tag. Example:

.. code-block:: xml

        <set xpath="//packages[@type='image']">
            profiles: some_profile
        </set>

.. warning::
    The content of the ``<set/>`` tag should be a proper and valid YAML, where its ident starts from the first line. Its content should always parse to a ``key: value`` format.

You can also derive derived image in a any new content description, e.g. ``editors.kiwi`` etc, and then add modifications on top of modified content description:

.. code-block:: xml

    <inherit path="emacs.kiwi"/>

This technique will allow you to have the same image content description with small deviations/modifications for different sub- use cases, while in "plain" Kiwi NG you would need to copy the whole appliance description every time.

Scripts, Overlays and Configuration
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

Currently Berrymill does not provide any framework with regard of deriving configuration scripts, because it is not very necessary. It can be done on your own just organising shell commands in a separate functions as a library and then including these snippets into your ``config.sh`` or any other hook.
