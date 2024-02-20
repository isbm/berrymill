.DEFAULT_GOAL := help

ARC_V := $(shell cat src/berry_mill/__init__.py | grep 'version = ' | sed -e 's/.*=//g' -e 's/[" ]//g')
ARC_N := berrymill-${ARC_V}

help:
	@printf 'Available commands:\n'
	@printf '\ttar    - make source tarfile for packaging and distribution\n'
	@printf '\tman    - generate manpages\n'
	@printf '\tbuild  - build Berrymill locally\n'

man:
	@echo TODO

tar:
	rm -rf package/${ARC_N}
	mkdir -p package/${ARC_N}
	for f in LICENSE README.md requirements.txt setup.cfg setup.py pytest.ini pyproject.toml; do \
		cp $$f package/${ARC_N} ; \
	done
	for d in src test doc config; do \
		cp -a $$d package/${ARC_N} ; \
	done

	for j in $$(find package -type d | grep __pycache__); do \
		rm -rf $$j ; \
	done

	rm -rf package/${ARC_N}/doc/build

	tar -C package -czvf package/${ARC_N}.tar.gz ${ARC_N}
	rm -rf package/${ARC_N}
