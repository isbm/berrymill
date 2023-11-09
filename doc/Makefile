PANDOC ?= pandoc

MANSECTION ?= 8

MANPAGE.md = $(PANDOC) --standalone $(PANDOCFLAGS) --to man

%.$(MANSECTION): %.$(MANSECTION).md
	$(MANPAGE.md) $< -o $@

all: berrymill.8
