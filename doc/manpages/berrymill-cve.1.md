%CVE(1) Version 0.3 | Berrymill Documentation

NAME
====

**cve** — plugin for intrusion detection and opened cve scanner

SYNOPSIS
========

| **cve** \[-h|\--help]

DESCRIPTION
===========

Plugin for the Berrymill framework, which scans specified image(s),
analysing any possible intrusions, finding out CVE numbers and their
status.

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
of the plugin, namely `cve`. Following is the list of top-level
configuration items.

Essentially, this plugin is taking care of setting up all the
necessary mounts of your image and then just calling **grype**[1] over partitions.

* `engine`

**NOTE: Subject to be obsolete and dropped.**

It only specifies what CVE scanner to use. It is always set to "grype".

* `verbose`

If set to "true", logging will have animated output, coming from
"grype" and will show all and complete progress. If set to "false",
then Berrymill will just wait until Grype is finished.

* `format`

Output format. It can be:

1. json
2. table
3. cyclonedx
4. cyclonedx-json
5. sarif
6. template

As of version 0.104.0, it still can also provide **deprecated** formats:

1. embedded-cyclonedx-vex-json
2. embedded-cyclonedx-vex-xml

**NOTE:** To have human-readable output, use format "table".

# OUTPUT

Resulting text files are placed next to the image, are named after the
image filename and its partition number, prefixed with the extension
of the format name itself.

# LINKS

1. Anchore Grype: https://github.com/anchore/grype

BUGS
====

See GitHub Issues: <https://github.com/isbm/berrymill/issues>

SEE ALSO
========

**berrymill**(1)
