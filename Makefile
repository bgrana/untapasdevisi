start:
	python untapasdevisi/core.py

db.reset: db.clear db.seed

db.seed:
	python seed.py

db.clear:
	mongo untapasdevisi --eval "db.dropDatabase();"