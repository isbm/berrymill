%WORKFLOW(1) Version 0.2 | Berrymill Documentation

NAME
====

**workflow** — plugin batch caller

SYNOPSIS
========

| **workflow** \[-h|\--help]

DESCRIPTION
===========

Plugin within Berrymill framework, which simply runs in a specified
order all the plugins.

FILES
=====

As any **berrymill** plugin, the whole configuration is in the common
`project.conf` file, which should be placed to the root of the current
project. This file contains all configuration for all possible plugins
and defines everything.

CONFIGURATION
=============

Configuration of the **workflow** plugin is very simple:

Example:

```
-general:
  images:
    - dir://path/to/all/the/images

plugin-name:
  ...

other-plugin-name:
  ...
  
workflow:
  - plugin-name
  - other-plugin-name
```

In the example above, section **-general** should have at least one
path where all examined images are located. And then **workflow**
option just contains a list of plugins, those are configured in the
same `project.file`.

Running this plugin will just call one plugin after another as simple
as this:

	berrymill workflow

BUGS
====

See GitHub Issues: <https://github.com/isbm/berrymill/issues>

SEE ALSO
========

**berrymill**(1)
