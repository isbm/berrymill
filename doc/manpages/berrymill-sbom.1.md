%SBOM(1) Version 0.3 | Berrymill Documentation

NAME
====

**sbom** — plugin for SBOM generation over OCI containers and images

SYNOPSIS
========

| **sbom** \[-h|\--help]

DESCRIPTION
===========

Plugin for the Berrymill framework, which scans specified image(s),
generating SBOM out of installed software components

This plugin is useful to have a good summary on the resulting image,
that is going to be flushed on mission critical hardware.

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
of the plugin, namely `sbom`. Following is the list of top-level
configuration items.

Essentially, this plugin is taking care of setting up all the
necessary mounts of your image and then just calling **syft**[1] over partitions.

* `engine`

**NOTE: Subject to be obsolete and dropped.**

It only specifies what SBOM generator to use. It is always set to "syft".

* `verbose`

If set to "true", logging will have animated output, coming from
"syft" and will show all and complete progress. If set to "false",
then Berrymill will just wait until Syft is finished.

* `format`

Output format. It can be one of the following:

1. cyclonedx-json
2. cyclonedx-xml
3. github-json
4. spdx-json
5. spdx-tag-value
6. syft-json
7. syft-table
8. syft-text
9. template

**NOTE:** To have human-readable output, use format "syft-table".

# OUTPUT

Resulting text files are placed next to the image, are named after the
image filename and its partition number, prefixed with the extension
of the format name itself.

# LINKS

1. Anchore Grype: <https://github.com/anchore/syft>

BUGS
====

See GitHub Issues: <https://github.com/isbm/berrymill/issues>

SEE ALSO
========

**berrymill**(1)
