run:
	bash run.sh

reqs:
	pip-compile requirements.in -o requirements.txt

reqs-dev:
	pip-compile requirements-dev.in -o requirements-dev.txt

reqs-all:
	$(MAKE) reqs
	$(MAKE) reqs-dev

sync:
	pip-sync requirements.txt

sync-dev:
	pip-sync requirements-dev.txt
