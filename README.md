# Berrymill

It is a wrapper around Kiwi Appliance Builder.

#### What is this name?

A [project KIWI](https://github.com/OSInside/kiwi), originally
supposed to be named after New Zealand citizen, ended up in the
community to be just a sour berry fruit. Hence the name: berry(fruit)
mill.

## Overview

**Berrymill** is an appliance generator of root filesystems for
embedded devices. It integrates Kiwi image builder to the
Ubuntu/Debian distributions, allowing building images locally.

## Use Cases

### Build an Image Locally

That can also KIWI do. Except if your image build also should
equally run on [OBS](https://openbuildservice.org) **and** locally
without image description changes.

### A Dozen of Small Deviations

You have one image that you do not change that often (or at all), but
you have little small deviations: add a package here, remove there,
change size, filesystem type etc. You don't want to have carbon copies
all around the place, but you want to have _derived images_.

### Configuration Management

Unlike plain KIWI, which keeps configuration in a straight-forward
fashion, Berrymill is also handling the Configuration Management in a
framework style.

## Limitations

Berrymill is in early development and some features might be missing
or not working properly. If that happens, please open a bug report by
[adding an issue here](https://github.com/isbm/berrymill/issues).
