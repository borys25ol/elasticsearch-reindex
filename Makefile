ve:
	test ! -d .ve && python3 -m venv .ve; \
	. .ve/bin/activate; \
	pip install -r requirements.txt; \

install_hooks:
	pip install -r requirements-ci.txt; \
	pre-commit install; \

clean:
	test -d .ve && rm -rf .ve

test:
	.ve/bin/python -m pytest .

run_hooks_on_all_files:
	pre-commit run --all-files

style:
	flake8 main && isort main --diff && black main --check

types:
	mypy --namespace-packages -p "elasticsearch_reindex" --config-file setup.cfg
