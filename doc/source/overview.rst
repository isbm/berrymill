.. berrymill overview

Overview
========

A system image, often called simply an "image," encapsulates a complete Linux system installation within a single file. This image essentially represents an entire operating system and, optionally, includes the final configuration settings.

In a process similar to Kiwi NG, Project Berrymill generates images through two distinct phases:

1. **Preparation**: During this stage, the system root tree is constructed based on the specifications provided in the image description.
2. **Rendering**: Here, the finalized image or the desired image format is produced using the prepared system root and the details outlined in the configuration file.

Terminology
-----------

This documentation largely employs terminology consistent with the `Kiwi NG <http://osinside.github.io/kiwi/>`_. However, there are specific differences to note:

Image:
    An **image** *(also known as "an appliance")* represents a pre-configured and fully prepared installation of an operating system and its associated applications, tailored for a specific use case. It's typically delivered in the form of a binary file and requires deployment or activation within the target system or service.

Content Description:
    To define an image, the **content description** consists of human-readable files within a directory. At least one XML file, either ``config.xml`` or ``.kiwi``, is essential. Additionally, supplementary files such as scripts or configuration data may be present. These elements serve to customize specific aspects of either the Berrymill build process or the initial startup behaviour of the image.

Overlay Data or Overlay Files:
    Within the Content Description, a directory structure contains files and subdirectories. This structure can be archived as a file named ``root.tar.gz`` or stored directly within a directory labelled *"root"*. It's also possible to incorporate additional overlay directories for specific profiles. These overlays are considered when the directory name corresponds to a profile name.

    Each directory structure's content is merged onto the current file system of the appliance root (overlayed). This process encompasses the transfer of permissions and attributes as a supplement to the existing file system.

Virtualisation:
    A virtual machine emulates computer hardware, functioning similarly to a real computer but operating independently from physical hardware. In this documentation, the QEMU virtualisation system is utilised. Another widely used alternative is VirtualBox. Both systems provide virtualised environments for running operating systems and applications without direct reliance on physical hardware.

System Requirements
-------------------

To efficiently utilise Project Berrymill, you'll need the following:

- Ubuntu or any recent Debian Linux distribution. Other distributions might also work but they are not tested.
- Sufficient free disk space, a minimum of **15GB**, for image building and storage.
- Python version **3.10** or higher.
- Git for repository cloning.
- Any supported virtualisation technology to initiate the image; we recommend **QEMU**.
