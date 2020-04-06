export TZ=Europe/London

test tests: unittests

unittests:
	@PYTHONPATH=. pytest --cov=nginxcfg --cov-report xml:cobertura.xml --cov-report term-missing

pycodestyle:
	@pycodestyle nginxcfg.py --config pycodestyle.cfg

pylint:
	@pylint --rcfile=pylint.cfg nginxcfg.py -j 4 -f parseable -r n 

clean:
	find . -name \*.pyc -delete
	rm -rf __pycache__ .cache .coverage
