Before You Start
----------------

Apart from basic Berrymill configuration, there is a workflow mechanism,
allowing to use various plugins, leveraging Berrymill features, such as
mounting images, tracking them, applying chain of plugins, integrate them etc.

Any plugin is configured in an additional configuration file, called
``project.conf``. This file should be placed to the root of the current
project, where typically ``appliance.kiwi`` XML file is also located.
This file contains all configuration for all plugins and defines their
routine such as their workflow and the details for each plugin separately.

The ``project.conf`` file has a top-level general section, called ``-general`` (note the prefix "-").
This section defines all the images, those needs to be post-processed by the plugins. Each list item
in the ``images`` is a directory path, starting with ``dir://`` schema, and telling Berrymill
where to look for the images.

.. warning::

  Image files can be only named with ``.qcow2`` or ``.raw`` file extensions.
  Any other files will be ignored!


The section ``images`` should always contain **at least one** (or more) path
of an image, against which all these plugins will be applied.

.. note::
    Scheme with two slashes like so ``dir://my/path`` refers to a *relative* path as ``my/path``.
    An absolute path like ``/my/path`` should have three slashes, like so: ``dir:///my/path``.

Example:

.. code-block:: yaml

    -general:
      images:
        - dir://at/least/one/path/to/my/images
        - dir://another/optional/path/to/my/images
        - dir:///this/is/an/absolute/path

To continue the configuration, any other plugin has their own section at the root level,
starting as the same **id** of the plugin. For example ``kern-hv`` or ``overlay`` etc.
