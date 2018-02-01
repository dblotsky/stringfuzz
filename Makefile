TOTAL     = $(shell find . 					     -name "*.py" | xargs cat | wc -l)
GEN       = $(shell find stringfuzz/generators   -name "*.py" | xargs cat | wc -l)
TRANS     = $(shell find stringfuzz/transformers -name "*.py" | xargs cat | wc -l)
NUM_TOTAL = $(shell find . 					     -name "*.py" | wc -l)
NUM_GEN   = $(shell find stringfuzz/generators   -name "*.py" | wc -l)
NUM_TRANS = $(shell find stringfuzz/transformers -name "*.py" | wc -l)
PER_TOTAL = $(shell echo $$(( $(TOTAL) / $(NUM_TOTAL) )) )
PER_GEN   = $(shell echo $$(( $(GEN) / $(NUM_GEN) )) )
PER_TRANS = $(shell echo $$(( $(TRANS) / $(NUM_TRANS) )) )

help default all usage:
	@echo "Usage: don't use."

loc:
	@echo "total:" $(TOTAL) / $(NUM_TOTAL) = $(PER_TOTAL)
	@echo "gen:  " $(GEN) / $(NUM_GEN)     = $(PER_GEN)
	@echo "trans:" $(TRANS) / $(NUM_TRANS) = $(PER_TRANS)

run:
	stringfuzzx --help
	stringfuzzg --help
	stringstats --help

test:
	python3 -m unittest tests/*.py

develop: test
	python3 setup.py develop

install:
	python3 -m pip install --upgrade pip setuptools wheel
	python3 setup.py install

uninstall:
	yes | pip3 uninstall stringfuzz

reinstall: uninstall install

clean:
	$(RM) *.pyc
	$(RM) -r ./**/__pycache__
	$(RM) -r build
	$(RM) -r dist
	$(RM) -r *.egg-info
