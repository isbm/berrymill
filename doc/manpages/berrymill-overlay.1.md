%OVERLAY(1) Version 0.3 | Berrymill Documentation

NAME
====

**overlay** — plugin for applying data artifacts over the existing rootfs

SYNOPSIS
========

| **overlay** \[-h|\--help]
| **overlay** \[-r|\--dir]

DESCRIPTION
===========

Plugin for the Berrymill framework, which allows to post-process the
existing partitions, applying any other possible configuration
artifacts. This can be in particular useful if the same image
derivative should have different configuration flavours.

FILES
=====

As any **berrymill** plugin, the whole configuration is in the common
`project.conf` file, which should be placed to the root of the current
project. This file contains all configuration for all possible plugins
and defines everything.

CONFIGURATION
=============

Working image(s) are always defined in the `project.conf` file at the
beginning of it, in the section `-general` (note the leading "minus")
and the list `images`. Each list item in the `images` is a directory
with `dir://` schema, telling Berrymill where to look for the
images. Image files can be only named with `.qcow2` or `.raw` file
extensions. The section `images` should contain **at least one**
path. Scheme `dir://my/path` refers to a *relative* path as `my/path`.
An absolute path should have three slashes, like `dir:///my/path`.

Example:

```
-general:
  images:
    - dir://at/least/one/path/to/my/images
    - dir://another/optional/path/to/my/images
	- dir:///this/is/an/absolute/path
```

As any other plugin, the specific section starts from the same **id**
of the plugin, namely `cve`. Following is the list of top-level
configuration items.

Essentially, this plugin is taking care of setting up all the
necessary mounts of your image and then just calling **grype**[1] over partitions.

# CONFIGURATION

The **overlay** plugin has two options:

* `roots`

This is a list of roots, those will be applied in the order they are
specified. Example:

```
roots:
  - dir://path/to/my/roots
```

* `partitions`

This is a list of partitions on which those roots will be
applied. Example:

```
partitions:
  - 2
```

NOTE: Currently overlay plugin **does not support** applying specific root on a
specific partition, but only applies "everything on everything".

BUGS
====

See GitHub Issues: <https://github.com/isbm/berrymill/issues>

SEE ALSO
========

**berrymill**(1)
