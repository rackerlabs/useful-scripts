export TZ=Europe/London

test tests: pylint pycodestyle

pylint:
	@pylint --rcfile=.pylintrc *.py -j 4 -f parseable -r n

pycodestyle:
	@pycodestyle --config=setup.cfg *.py

clean:
	find . -name \*.pyc -delete
	rm -rf __pycache__ .cache

