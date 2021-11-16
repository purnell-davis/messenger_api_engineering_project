#
# Makefile
#
# Run, test and "build" messenger_api project.
#

setup:
	# Create virtual environment
	virtualenv .venv
	. .venv/bin/activate

env:
	# Show information about environment
	which python3
	python3 --version
	which pytest
	which pylint

lint:
	# Code Quality
	pylint messenger_db.py --disable=R0903

test:
	# Functional Tests and Code Coverage
	PYTHONPATH=. pytest -vv --cov tests/

install:
	# Install necessary dependencies
	pip3 install -r requirements.txt 

example-setup:
	# Create example DB data.
	PYTHONPATH=. python3 tests/example_setup.py

start-api:
	# Run the flask app
	FLASK_ENV=development FLASK_APP=messenger_app flask run

all: install lint test
