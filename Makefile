NOSETESTS="nosetests-3"

test:
	PYTHONPATH=core/bundle $(NOSETESTS) -w tests -v
