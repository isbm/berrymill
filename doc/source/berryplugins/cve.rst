Plugin "cve"
----------------

.. note::
    Description of a plugin for the Berrymill framework.
    This plugin might be not available in your particular installation.

Plugin for the Berrymill framework, which scans specified image(s),
analysing any possible intrusions, finding out CVE numbers and their
status.

This plugin is useful to have a good summary on the resulting image,
that is going to be flushed on mission critical hardware.

Configuration
=============

Essentially, this plugin is taking care of setting up all the
necessary mounts of your image and then just calling `Anchore Grype <https://github.com/anchore/grype>`_
over the registered partitions if it makes sense.

``engine``

.. warning::

    This option is subject to be considered obsolete and therefore dropped.

It only specifies what CVE scanner to use. It is always set to "grype".

``verbose``
  If set to "true", logging will have animated output, coming from
  "grype" and will show all and complete progress. If set to "false",
  then Berrymill will just wait until Grype is finished.

``format``
  Output format. It can be:

  1. ``json``
  2. ``table``
  3. ``cyclonedx``
  4. ``cyclonedx-json``
  5. ``sarif``
  6. ``template``

  As of version **0.104.0**, it still can also provide **deprecated** formats:

  1. ``embedded-cyclonedx-vex-json``
  2. ``embedded-cyclonedx-vex-xml``

.. hint::

  To have human-readable output, please use format ``table``.

Output
======

Resulting text files are placed next to the image, are named after the
image filename and its partition number, prefixed with the extension
of the format name itself.
