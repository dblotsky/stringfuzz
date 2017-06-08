help default all usage:
	@echo "Usage: don't use."

run:
	smtfuzzx --help
	smtfuzzg --help
	smtstats --help

test:
	python3 -m unittest tests/*.py

develop: test
	python3 setup.py develop

install:
	python3 setup.py install

uninstall:
	yes | pip3 uninstall smtfuzz

reinstall: uninstall install

clean:
	$(RM) *.pyc
	$(RM) -r ./**/__pycache__
	$(RM) -r build
	$(RM) -r dist
	$(RM) -r *.egg-info
