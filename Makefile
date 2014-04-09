start:
	python untapasdevisi/core.py

install:
	pip install -r requirements.txt

lint:
	flake8 untapasdevisi tests

test: lint
	nosetests

db.reset: db.clear db.seed

db.seed:
	python seed.py

db.clear:
	mongo untapasdevisi --eval "db.dropDatabase();"