# Run pytest and generate coverage.
pytest -v --cov=studio --cov-report=html --cov-report=xml -s tests/


# Open up the coverage report.
# python -m http.server --directory htmlcov/