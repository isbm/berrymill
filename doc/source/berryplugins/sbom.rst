Plugin "SBOM generator"
-----------------------

.. note::
    Description of a plugin for the Berrymill framework.
    This plugin might be not available in your particular installation.

Plugin for the Berrymill framework, which scans specified image(s)
and generates SBOM data out of installed software components on the image.

This plugin is useful to have a good summary on the resulting image,
that is going to be flushed on mission critical hardware.

Configuration
=============

Essentially, this plugin is taking care of setting up all the
necessary mounts of your image and then just calling `Anchore Syft <https://github.com/anchore/syft>`_
over the registered partitions if it makes sense.

``engine``

.. warning::

    This option is subject to be considered obsolete and therefore dropped.

It only specifies what CVE scanner to use. It is always set to "syft".

``verbose``
  If set to "true", logging will have animated output, coming from
  "syft" and will show all and complete progress. If set to "false",
  then Berrymill will just wait until Syft is finished.

``format``
  Output format. It can be one of the following:

  1. ``cyclonedx-json``
  2. ``cyclonedx-xml``
  3. ``github-json``
  4. ``spdx-json``
  5. ``spdx-tag-value``
  6. ``syft-json``
  7. ``syft-table``
  8. ``syft-text``
  9. ``template``


.. hint::

  To have human-readable output, please use format ``syft-table``.

Output
======

Resulting text files are placed next to the image, are named after the
image filename and its partition number, prefixed with the extension
of the format name itself.
