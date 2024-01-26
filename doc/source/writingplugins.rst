Writing Own Plugin
==================

Plugins Location
----------------

Plugins are all located as subdirectory of ``berry_mill`` site-package of your current Python installation.

Requirements
------------

A plugin should implement ``berry_mill.plugin.PluginIf`` abstract class (interface) the following methods:

.. code-block:: python

    def run(self):

This method is to ``run`` the plugin, assuming all arguments are already passed through.

.. code-block:: python

    def setup(self, *args, **kw):

This method is for some extra manual setup, when ``autosetup`` is still not enough.

Plugin Registration
-------------------

In plugin's ``__init__.py`` one needs to register the plugin, using ``berry_mill.plugin.registry`` like so:

.. code-block:: python

    registry(YourPluginClass(title="Example plugin",
                             name="yourplugin",
                             argmap=argmap))

The arguments map is a list of ``berry_mill.plugin.PluginArgs`` objects, each represents a CLI argument. For example:

.. code-block:: python

    argmap = [
        PluginArgs("-v", "--version", help="Display version")
        PluginArgs("-h", "--help", help="Display help"),
    ]

The ``argmap`` then can be passed to the registry as in example above. To know more how to construct arguments, simply refer to the standard ``argparse`` module. The semantics are preserved.

How To Distribute Plugins
-------------------------

Given that all plugins are just a subdirectory in ``berry_mill`` site-package of current Python, adding the entire plugin into that directory is sufficient. Distribution can be manual or via packaging.