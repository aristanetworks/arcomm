.PHONY: docs

init:
    pip install -r requirements.txt

test:
    # This runs all of the tests. To run an individual test, run py.test with
    # the -k flag, like "py.test -k test_path_is_not_double_encoded"
    py.test test_requests.py

coverage:
    py.test --verbose --cov-report term --cov=requests test_requests.py

ci: init
    py.test --junitxml=junit.xml

publish:
    python setup.py register
    python setup.py sdist upload
    python setup.py bdist_wheel upload

docs-init:
    pip install -r docs/requirements.txt

docs:
    cd docs && make html
    @echo "\033[95m\n\nBuild successful! View the docs homepage at docs/_build/html/index.html.\n\033[0m"
