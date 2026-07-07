# --
.PHONY: update
update:
	uv self update
	uv sync --upgrade
	uv lock --upgrade

# --
.PHONY: docs docs-api docs-user
docs: docs-api docs-user

docs-api:
	rm -rf docs/api/source/
	uv run sphinx-apidoc -f -o docs/api/source/ . -d 3 --tocfile=index --module-first --separate
	uv run sphinx-build -M clean docs/api/source/ docs/api/build --conf-dir docs/api/
	uv run sphinx-build -M html docs/api/source/ docs/api/build --silent --conf-dir docs/api/

docs-user:
	uv run sphinx-build -M clean docs/manual/source/ docs/manual/build --conf-dir docs/manual/
	uv run sphinx-build -M html docs/manual/source/ docs/manual/build --conf-dir docs/manual/

# --
prospector:
	@uv run prospector -W mccabe ..

# --
config_file = ../config.ini
a.ini:
	PYTHONPATH=.. uv run ./test.py -c $(config_file) -t ./test_case/$@

test-All.ini:
	PYTHONPATH=.. uv run ./test.py -c $(config_file) -t ./test_case/$@

test-FileGeneration.ini:
	PYTHONPATH=.. uv run ./test.py -c $(config_file) -t ./test_case/$@

test-LastMonth.ini:
	PYTHONPATH=.. uv run ./test.py -c $(config_file) -t ./test_case/$@

test-OutOfScope.ini:
	PYTHONPATH=.. uv run ./test.py -c $(config_file) -t ./test_case/$@

test-Report.ini:
	PYTHONPATH=.. uv run ./test.py -c $(config_file) -t ./test_case/$@

test-ThisMonth.ini:
	PYTHONPATH=.. uv run ./test.py -c $(config_file) -t ./test_case/$@

test-anonymous.ini:
	PYTHONPATH=.. uv run ./test.py -c $(config_file) -t ./test_case/$@

test-groupby.ini:
	PYTHONPATH=.. uv run ./test.py -c $(config_file) -t ./test_case/$@

test-help.ini:
	PYTHONPATH=.. uv run ./test.py -c $(config_file) -t ./test_case/$@

test-individual.ini:
	PYTHONPATH=.. uv run ./test.py -c $(config_file) -t ./test_case/$@

test-rating.ini:
	PYTHONPATH=.. uv run ./test.py -c $(config_file) -t ./test_case/$@

test-team.ini:
	PYTHONPATH=.. uv run ./test.py -c $(config_file) -t ./test_case/$@

test-saki:
	PYTHONPATH=.. uv run ./test.py -c ./test_data/saki.ini -t ./test_data/test_pattern01.ini
