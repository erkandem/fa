
run:
	python app.py

run-prod:
	bash run.sh

reqs:
	pip-compile requirements.in -o requirements.txt

reqs-dev:
	pip-compile requirements-dev.in -o requirements-dev.txt

reqs-all:
	$(MAKE) reqs
	$(MAKE) reqs-dev


install:
	pip install -r requirements.txt --ignore-installed

install-dev:
	pip install -r requirements-dev.txt --ignore-installed

sync:
	pip-sync requirements.txt

sync-dev:
	pip-sync requirements-dev.txt

locust:
	locust -f locust_file.py --host=http://0.0.0.0:5000

gunicorn:
	gunicorn -b 0.0.0.0:5000 -w 4 -k uvicorn.workers.UvicornWorker app:app

test:
	IVOLAPI_TESTING=true pytest
