start:
	python untapasdevisi/core.py

install:
	pip install -r requirements.txt

lint:
	flake8 untapasdevisi tests

test: lint
	nosetests

loc:
	grep -Rv --exclude-dir=venv --include "*.py" --include "*.js" --include "*.html" --include "*.css" "^\s*$$" | wc -l

db.reset: db.clear db.seed

db.seed:
	python seed.py

db.clear:
	mongo untapasdevisi --eval "db.dropDatabase();"