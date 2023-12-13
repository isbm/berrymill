SPHINXOPTS    ?=
SPHINXBUILD   ?= sphinx-build
SOURCEDIR     = source
BUILDDIR      = build
MANPAGES      ?= manpages

.ONESHELL:
.SILENT:

.PHONY: help Makefile

help:
	@$(SPHINXBUILD) -M help "$(SOURCEDIR)" "$(BUILDDIR)" $(SPHINXOPTS) $(O)
	cat << EOF
	Additionally, use these commands:
	docs  		Generate documentation (Sphinx)
	man-ext		Generate extra manpage
	all 		Run documentation
	EOF

# Catch-all target: route all unknown targets to Sphinx using the new
# "make mode" option.  $(O) is meant as a shortcut for $(SPHINXOPTS).
%: Makefile
	@$(SPHINXBUILD) -M $@ "$(SOURCEDIR)" "$(BUILDDIR)" $(SPHINXOPTS) $(O)

docs:
	@echo "Generating HTML documentation"
	@$(SPHINXBUILD) -M html "$(SOURCEDIR)" "$(BUILDDIR)" $(SPHINXOPTS) $(O)

man-ext:
	@echo "Generating extra manpages..."
	pandoc --standalone $(PANDOCFLAGS) --to man $(MANPAGES)/berrymill.8.md -o $(MANPAGES)/berrymill.8
	@echo "Extra manpages in 'manpages' subdirectory"
