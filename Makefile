test:
	# use a nested shell to resolve path to nosetests and run the path with python3
	# so that we don't need to change the executable name every time major version
	# of Python changes in the distro
	nosetests-3 -w tests -v
