Plugin "Workflow"
-----------------------

.. note::
    Description of a plugin for the Berrymill framework.
    This plugin might be not available in your particular installation.

Plugin within Berrymill framework, which simply runs in a specified
order all the plugins.

Configuration
=============

Configuration of the **workflow** plugin is very simple. For example:

.. code-block:: yaml

  -general:
    images:
      - dir://path/to/all/the/images

  # The usual configuration of "plugin-name" plugin
  plugin-name:
    ...

  # The usual configuration of "other-plugin-name" plugin
  other-plugin-name:
    ...

  # Just specify the order
  workflow:
    - plugin-name
    - other-plugin-name


In the example above, section ``-general`` should have at least one
path where all examined images are located. And then ``workflow``
option just contains a list of plugins, those are configured in the
same ``project.file``.

Running this plugin will just call one plugin after another as simple
as this:

.. code-block:: bash

	berrymill workflow
