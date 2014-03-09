run:
	python untapasdevisi/core.py

count-loc:
	grep -Rv --exclude-dir=venv --include "*.py" --include "*.js" --include "*.html" --include "*.css" "^\s*$$" | wc -l