start:
	python untapasdevisi/core.py

clear-db:
	mongo untapasdevisi --eval "db.dropDatabase();"