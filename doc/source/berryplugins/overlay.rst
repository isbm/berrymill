Plugin "overlay"
----------------

.. note::
    Description of a plugin for the Berrymill framework.
    This plugin might be not available in your particular installation.

The **overlay** plugin is designed to apply random data artifacts over the existing rootfs,
which allows to post-process the existing partitions, applying any other possible configuration
artifacts. This can be in particular useful if the same image
derivative should have different configuration flavours.

.. warning::
    Currently the image filesystem should be able to be mounted as read-write. Conversion between
    read-only images (SquashFS) are not yet supported. **This plugin is in early development stage**.

    Your pull request `to this Git repository <https://github.com/isbm/berrymill>`_ would speed it up! 😊

Configuration
=============

The **overlay** plugin has two configuration sections:

``roots``
  This is a list of roots, those will be applied in the order they are specified. Example:

  .. code-block:: yaml

    roots:
      - dir://path/to/my/roots

``partitions``
  This is a list of partitions on which those roots will be applied. Example:

  .. code-block:: yaml

    partitions:
      - 2  # Apply everything on partition No. 2

.. note::
  Currently overlay plugin **does not support** applying specific root on a
  specific partition, but only applies "everything on everything".
