# TODO: add builder
FROM python:3.9.16-slim

ENV PIPENV_VENV_IN_PROJECT=1 PYTHONDONTWRITEBYTECODE=1 PYTHONUNBUFFERED=1 PIP_DISABLE_PIP_VERSION_CHECK=1 PIP_NO_CACHE_DIR=1
ENV PIPENV_CACHE_DIR=/tmp/cache
# install pipenv
RUN pip install --user pipenv

# move Pipfiles into working directory
ADD Pipfile.lock Pipfile /usr/src/
WORKDIR /usr/src

# download all packages
RUN /root/.local/bin/pipenv sync

ADD src ./
CMD [".venv/bin/python", "-m", "gunicorn", "-b", "0.0.0.0:5000", "-w", "2", "predictor:get_app()"]