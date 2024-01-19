Configuration
=============

Configuration file can be selected with berrymill option ``--config`` or ``-c``, otherwise default configuration file ``/etc/berrymill/berrymill.conf`` is used. It has:

``repos`` repositories setup which has:

Architecture ``amd64`` or/and ``arm64``.
Distro e.g. ``Ubuntu-Jammy``.
``url`` e.g. ``http://ports.ubuntu.com``.
``type`` e.g. ``apt-get``.
``key`` GPG key.
``name`` distro name.
``components`` e.g. ``main,universe,multiverse,restricted``.

In addition, ``use-global-repos`` which is boolean to enable/disable global repositories usage.
``boxed_plugin_conf`` kiwi boxed plugin configuration path.

Example berrymill configurations can be found at ``berrymill/config/berrymill.conf.example``.
