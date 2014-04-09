start:
	python untapasdevisi/core.py

install:
	pip install -r requirements.txt

db.reset: db.clear db.seed

db.seed:
	python seed.py

db.clear:
	mongo untapasdevisi --eval "db.dropDatabase();"