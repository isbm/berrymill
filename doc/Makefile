SPHINXOPTS  ?=
SPHINXBUILD ?= sphinx-build
SOURCEDIR   = .
BUILDDIR    = _build
MANPAGES    ?= manpages

.ONESHELL:
.SILENT:
.PHONY: help

%: all man

help:
	cat << EOF
	docs	Generate documentation (Sphinx)
	man	Generate manpages
	all	Run everything
	EOF

man:
	@echo "Generating manpages..."
	pandoc --standalone $(PANDOCFLAGS) --to man $(MANPAGES)/berrymill.8.md -o $(MANPAGES)/berrymill.8

docs:
	@echo "Generating documentation..."
