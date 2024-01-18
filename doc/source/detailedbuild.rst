Building Image
==============

.. note::
    This page explains the details about building images with Berrymill.

Build Types
-----------

Local Build
^^^^^^^^^^^

To build your image locally, execute the following command:

.. code-block:: shell

    $ berrymill -i path/to/descr.kiwi/or/config.xml --profile Disk build -l --target-dir=/tmp/foo

``--image`` or ``-i`` is used to specify the image appliance. ``--profile`` or ``-p`` is used to select the profile, e.g. Disk, Live, or Virtual.
The argument ``-l`` or ``--local`` is used to build image locally (on the current hardware).
The resulting image will be placed into directory ``/tmp/foo`` with the suffix ``.raw`` or ``qcow2`` or ``iso``.

Unless you specify a configuration with ``--config`` or ``-c``, default berrymill configuration is used, which is located at ``/etc/berrymill/berrymill.conf``.

Without ``-l``, the command above runs a box build (QEMU VM).

Cross Build
^^^^^^^^^^^

Cross build uses box build (QEMU VM). To cross build you need ``--cross`` argument. e.g.

.. code-block:: shell

    $ berrymill -i path/to/descr.kiwi/or/config.xml build --cross --target-dir=/tmp/foo

For both builds, debugging messages can be enabled with ``--debug`` or ``-d`` argument. In addition, ``--clean`` argument can be used to run a clean build (to remove the target directory before building if it exists).

``--cpu`` is used to select the cpu to be used by QEMU. By default, the host cpu type is used which is good if the host and the box have the same architecture. For cross builds it's required to specify the cpu, otherwise ``cortex-a57`` is used by default in case cross building on ``x86_64`` machine.

Berrymill configuration example can be found on ``berrymill/config/berrymill.conf.example``. Image appliances examples can be found on github at ``https://github.com/OSInside/kiwi-descriptions``.
