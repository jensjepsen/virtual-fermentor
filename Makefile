ACTIVATE=$(shell echo "`pwd`/venv/bin/activate")
PYTHON=$(shell echo "`pwd`/venv/bin/python")
PIP=$(shell echo "`pwd`/venv/bin/pip")

venv/touchfile:
	python3 -m venv venv
	$(PIP) install -r requirements.txt
	touch venv/touchfile

run: venv/touchfile
	cd src && $(PYTHON) -m uvicorn app:app --reload