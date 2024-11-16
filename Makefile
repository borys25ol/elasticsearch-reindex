ve:
	test ! -d .ve && python3 -m venv .ve; \
	. .ve/bin/activate; \
	pip install -r requirements.txt; \

install_hooks:
	pip install -r requirements-ci.txt; \
	pre-commit install; \

docker_build:
	docker-compose up -d --build

docker_up:
	docker-compose up -d

run_hooks:
	pre-commit run --all-files

test:
	python -m pytest -v ./tests

test-cov:
	python -m pytest  --cov=./elasticsearch_reindex --cov-report term-missing ./tests

style:
	flake8 elasticsearch_reindex && isort elasticsearch_reindex --diff && black elasticsearch_reindex --check

lint:
	flake8 elasticsearch_reindex && isort elasticsearch_reindex && black elasticsearch_reindex

types:
	mypy --namespace-packages -p "elasticsearch_reindex" --config-file setup.cfg
