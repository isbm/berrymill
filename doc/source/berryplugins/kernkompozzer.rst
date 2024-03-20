Plugin "kern-hv"
----------------

.. note::
    Description of a plugin for the Berrymill framework.
    This plugin might be not available in your particular installation.

Plugin for the Berrymill framework, which is designed to construct
booting image on QEMU or hardware, including a l4re Hypervisor from
`Kernkonzept <l4re Hypervisor: https://github.com/kernkonzept/l4re-core>`_.

The **kern-hv** plugin can be used alone separately, or can be chained
within the **workflow** plugin.

Configuration
=============

As any **berrymill** plugin, the whole configuration is in the common
``project.conf`` file, which should be placed to the root of the current
project. This file contains all configuration for all possible plugins
and defines everything.

Working image(s) are always defined in the ``project.conf`` file at the
beginning of it. At the beginnin, in general section which is called ``-general``
*(note the leading "minus")* and the list ``images``. Each list item in the ``images``
is a directory with ``dir://`` schema, telling Berrymill where to look for the
images. Image files can be only named with ``.qcow2`` or ``.raw`` file
extensions. The section ``images`` should contain **at least one**
path.

.. warning::
    Scheme with two slashes like so ``dir://my/path`` refers to a *relative* path as ``my/path``.
    An absolute path like ``/my/path`` should have three slashes, like so: ``dir:///my/path``.

Example:

.. code-block:: yaml

    -general:
      images:
        - dir://at/least/one/path/to/my/images
        - dir://another/optional/path/to/my/images
        - dir:///this/is/an/absolute/path

As any other plugin, the specific section starts from the same **id**
of the plugin, namely ``kern-hv``.

Top-level configuration sections
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

Following is the list of top-level
configuration items:

``output-dir``
  The ``output-dir`` is an optional item and defines subdirectory name,
  located in the same directory as ``project.conf`` file.

  Default value is ``build`` and refers that during the image build will
  be created a subdirectory ``build`` in the same place where ``project.conf`` is.

``output-image``
  The ``output-image`` is a filename of the resulting image, which will be
  placed in the ``output-dir`` destination alongside with other artefacts.

``hypervisor``
  This section is for hypervisor data configuration. It requires many
  different items, such as bootstrap image, the device tree files, Lua
  scripts and other artifacts.

``image-map``
  Section ``image-map`` is a technically any *key* to any *value*, and
  only defines symlinks to the already known image, those are scanned
  prior in the ``-general`` section. For example, if the hypervisor is
  configured to write ``example.raw`` image and in ``-general`` section is
  found a system, like ``demo-image.aarch64-1.0.raw``, then in order to
  hypervisor pick it up, it should be configured like so:

  .. code-block:: yaml

    image-map:
      example.raw: demo-image.aarch64-1.0.raw

  In this case, ``example.raw`` will be just a symlink to the
  ``demo-image.aarch64-1.0.raw`` file in temporary build directory.

The ``hypervisor`` section
^^^^^^^^^^^^^^^^^^^^^^^^^^

This option has four sections that puts together the main hypervisor
configuration.

``bootstrap-image``
  An original, default bootstrap U-Boot image, which is going to be
  repackaged with your configuration.

``device-tree``
  Directory where all device tree and metadata is located.

``hv-conf``
  Path to the directory, containing configuration in Lua scripts.

``hv-conf-entry``
  Name of the main entry in the metadata dependencies file.

The ``part-data`` section
^^^^^^^^^^^^^^^^^^^^^^^^^

This is a *key/value* mapping and should correspond to the configuration
in Lua scripts. Please refer to the Kernkonzept configuration
documentation to know more details.

Those files are usually used for VM partitions, those can be
many. Same as ``image-map``, the ``part-data`` option refers to the
following schema:

.. code-block:: yaml

    desired_filename: file://path/to/an/actual/filename


Usually the hypervisor expects Linux kernel and ``initrd`` file per a
partition. So in the Lua scripts one would usually configure those
files before starting a VM, such as ``my_ramdisk`` and
``my_kernel``. Therefore the configuration would look like this:

.. code-block:: yaml

    part-data:
      my_ramdisk: file:///path/to/my-image-1.0.initrd
      my_kernel: file:///path/to/my-image-1.0.kernel


The ``image-layout`` section
^^^^^^^^^^^^^^^^^^^^^^^^^^^^

.. note::
    Configuration of this section is not covered in the current document.

This option refers to the separate ``embdgen`` library and `has its own
documentation <https://elektrobit.github.io/embdgen>`_, available online. Either refer to it or read `embdgen` manpage.
