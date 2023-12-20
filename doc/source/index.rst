.. Berrymill documentation master file

Welcome to Berrymill documentation!
===================================

.. warning::
   This documentation focuses on Berrymill |version|, a tool designed to produce multiple images. Project Berrymill serves as **an extension** of `Kiwi NG <http://osinside.github.io/kiwi/>`_, therefore this documentation is also only an extension.

   ⚠️ Reader of this documentation is **required** to be familiar with the `Kiwi NG features <http://osinside.github.io/kiwi/>`_!

.. toctree::
   :maxdepth: 1

   overview
   installation
   quickstart
   configuration
   detailedbuild

Concept
-------

When installing an operating system onto hardware, one approach involves flashing an image that contains all the essential components. This image is pre-configured for specific use cases and is typically provided in the form of a binary file. The process involves deploying or activating this image on the target system or service.

Project Berrymill offers versatility in creating appliances, including classical installation ISOs, images for virtual machines, and bootable PXE images. Appliance configurations in Berrymill are defined by a set of human-readable files contained within a directory, known as the image description. To define an appliance, at least one XML file (``config.xml``) or a ``.kiwi`` file is necessary. Furthermore, additional files like scripts or configuration data may be included as needed.

Use Cases
---------

Under the hood, Project Berrymill operates on the foundation of `Kiwi NG <http://osinside.github.io/kiwi/>`_, therefore it inherits and maintains the same use cases as Kiwi NG does, which include:

- Cloud-based systems
- Custom Linux distributions
- Live systems
- Embedded Systems
- And more

The primary emphasis (and therefore difference) of Project Berrymill is leveraging the workflow advantages offered by `Yocto Project <https://www.yoctoproject.org>`_. This capability allows for the creation of various iterations of the same image, tailored for different specific use cases or hardware configurations.

Moreover, Berrymill offers developers the ability to:

- Manage various iterations of the same image
- Track and manage diverse configurations for identical images
- Execute identical appliance descriptions seamlessly both locally and on the `Open Build Service <https://openbuildservice.org>`_ without requiring modifications to the original appliance description.
