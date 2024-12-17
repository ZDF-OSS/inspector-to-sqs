.PHONY: start install

install:
	pip install -r requirements.txt

start: install
	python inspector_to_sqs.py
