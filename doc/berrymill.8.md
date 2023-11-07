% BERRYMILL(8) Version 1.0 | Berrymill Documentation

NAME
====

**berrymill** — generate a root file system for embedded devices

SYNOPSIS
========

| **berrymill** \[-h|\--help]
| **berrymill** \[global options] action \<command\> \[\<args>]
| **berrymill** \[-h] \[-s] \[-d] \[-a ARCH] \[-c CONFIG] -i IMAGE \[-p PROFILE] \[\--clean] \{prepare, build}  

DESCRIPTION
===========

**berrymill** is an appliance generator of root file systems for embedded devices.
It is a wrapper around **kiwi**(8) and allows to build images equally on
[OBS](https://openbuildservice.org) **and** locally without changes to the
image description.

Also it implements the concept of _derived images_ to extend kiwi image
descriptions with small derivations like adding or removing packages, changing
the size or the type of a file system. To do so simply create a xml file
that inherits the original image description (or an already derived one) and
add wanted content.

```

<?xml version="1.0" encoding="utf-8"?>
<image schemaversion="6.8" name="Testname">
    <inherit path="config.xml"/>

    ....
</image>

```

See a more complex example under EXAMPLES.

OPTIONS
=======

For **berrymill** the following options are available, irrespective if *prepare*
or *build* is chosen:

-h, --help

: Prints brief usage information.

-s, \--show-config

: Show the build configuration. The default configuration used by **berrymill**
resides in */etc/berrymill/berrymill.conf*. Alternative configurations can be
loaded with **-c**. See below as well.

-d, \--debug

: Turns on verbose debugging mode for **berrymill.** It will also pass
**\--box-debug** to the boxbuild.

-a ARCH, \--arch ARCH

: Sets target architecture e.g., aarch64.

-c CONFIG, \--config CONFIG

: Specify a configuration file other than default one. Expects a configuration
file as argument. Read more about the structure of configuration files in
section [FILES](#files).

-i IMAGE, \--image IMAGE

: Path to the image description, this parameter is required.
For more information on kiwi consult **kiwi**(8).

-p PROFILE, \--profile PROFILE

: Select a profile from the image description. If more than one is provided
in the image description and this parameter is not provided the build will
fail.


\--clean

: When \--clean is passed **berrymill** will cleanup previous build results like
the target directory.


When **berrymill** is executed with the option *prepare*  to prepare the sysroot
the following options are additionally available.

\--root ROOT

: Specifies path where the root system shall be created. This is passed along
to **kiwi::system::prepare**(8). This parameter is required for *prepare*.

\--allow-existing-root

: Allow to re-use an existing image root directory. This parameter is passed
along to **kiwi::system::prepare**(8).  


When **berrymill** is executed with the option *build*  to build the image the
following options are additionally available.

\--box-memory BOX\_MEMORY

: Specify amount of memory to be used by qemu for the boxbuild. The default is
*8G*. This parameter is passed to **kiwi::system::boxbuild**(8).

\--cpu CPU

: Specify CPU type to be used by qemu for the boxbuild. Per default the host
CPU is used. This parameter is passed to **kiwi::system::boxbuild**(8).
This option has no effect in combination with \--cross, as \--cross overwrites
this setting to an appropriate one.

\--cross

: Select \--cross to cross build an image on a x86\_64 host to an aarch64
target.

-l, \--local

: If -l, \--local is selected a local image build on the current architecture
is performed instead of a boxbuild. This will require sudo rights and an
installation of the KIWI tool chain.

\--target-dir TARGET\_DIR

: Specifiy the directory where the results of the build shall be placed by
**berrymill**. This parameter is required and gets passed along to
**kiwi**(8).

\--no-accel

: Disables the KVM acceleration for boxbuild.

\--ignore-nested

: Ignore warning that nested virtualization is not enabled.

FILES
=====

*/etc/berrymill/berrymill.conf*

This file defines the repositories that **berrymill** uses to build the image.
An example structure is given in the following.

```
ops-api: <api_url> 

use-global-repos: false
boxed_plugin_conf: <path_to_boxplugin_conf> 
repos:
  release:
    <architecture_1>
      Ubuntu-Jammy:
        url:  <repo_url>
        type: <repo_type>
        name: <name>
        components: main,universe,...

      ...
    <architecture_2>
...
```        

*/etc/berrymill/kiwi_boxed_plugin.yml*

Contains further configuration for the boxes to be used for the boxbuild.
See also **kiwi::system::boxbuild**(8)

EXAMPLES
========

1. Run a build on current architecture

```
sudo berrymill -d -i <image_descr> build -l --target-dir ./result
```

2. Run a cross build for aarch64

```
berrymill -d -i <image_descr> build --target-dir ./result
```

3. Derived configuration

```
<?xml version="1.0" encoding="utf-8"?>
<image schemaversion="6.8" name="test">
    <inherit path="config.xml"/>

    <!--
        Remove specific data. Anything inside of the "remove"
        tag should precisely match by attributes.
    -->
    <remove>
        <!--
            Remove a specific package, as only
            the last element is removed, while parents are
            just "qualifiers" to set the proper matching.
        -->
        <packages type="oem">
            <package name="dracut-kiwi-oem-dump"/>
        </packages>

        <!-- Remove the entire aggregate -->
        <packages type="iso" />
    </remove>

    <!--
        Remove any data. Anything inside of the "remove_any"
        tag should at least match by attributes. The less
        specific attributes, the higher is glob matcher.
    -->
    <remove_any>
        <!-- This will remove any "repository" tag that has these attributes -->
        <repository components="main multiverse restricted universe"/>
    </remove_any>

    <!-- Add specific data -->
    <add>
        <packages type="image">
            <package name="package"/>
        </packages>
    </add>

    <!--
        Replace and merge works only on aggregates.
        For individual tags e.g. "<repository/>", it should be first
        removed, then added back.
    -->
    <merge>
        <description type="system">
            <author>Herr Starr</author>
            <license>GLWTS</license>
        </description>
    </merge>

    <!-- This replaces the end-tag without XPath -->
    <replace>
        <packages type="oem">
            <package name="some-package"/>
        </packages>
    </replace>

    <set xpath="//user[@name='root' and @groups='root']">
        pwdformat: plain
        password: linux
    </set>
</image>
```

BUGS
====

See GitHub Issues: <https://github.com/isbm/berrymill/issues>

SEE ALSO
========
**kiwi**(8)
