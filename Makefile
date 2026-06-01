.PHONY: validate run-sample test clean-sample

PYTHON ?= python3
SAMPLE_OUTBOX ?= /tmp/icp-incubator-sample

validate:
	$(PYTHON) scripts/validate_csv.py examples/sample-accounts.csv
	$(PYTHON) scripts/validate_drafts_json.py examples/sample-drafts.json
	$(PYTHON) -m unittest discover -s tests

run-sample:
	rm -rf $(SAMPLE_OUTBOX)
	$(PYTHON) scripts/run_pipeline.py examples/sample-accounts.csv --outbox $(SAMPLE_OUTBOX)
	$(PYTHON) scripts/validate_drafts_json.py $(SAMPLE_OUTBOX)/drafts.json

test:
	$(PYTHON) -m unittest discover -s tests

clean-sample:
	rm -rf $(SAMPLE_OUTBOX)
